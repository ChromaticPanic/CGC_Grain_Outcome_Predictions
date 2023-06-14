from copy import deepcopy
import torch # need to install
import torch.nn as nn # need to install
from torch.utils.data import DataLoader, Dataset # need to install
from torch.autograd import Variable # need to install
from torch.optim import Adam # need to install
import numpy as np
import wandb # need to install

batch_size = 32
reconstruct_epoch = 300
epoch = 1000
num_encoded_features = 16

class TorchDataset(Dataset): # needs to rework when having the finalized data
    def __init__(self, inputs, targets):
        self.inputs = torch.from_numpy(inputs)
        self.targets = torch.from_numpy(targets)

        assert self.inputs.shape[0] == self.targets.shape[0]

    def __len__(self):
        return self.inputs.shape[0]

    def __getitem__(self, index):
        X = self.inputs[index]
        y = self.targets[index]

        return X, y


class OnlyXDataset(Dataset): # needs to rework when having the finalized data
    def __init__(self, inputs):
        self.inputs = torch.from_numpy(inputs)

    def __len__(self):
        return self.inputs.shape[0]

    def __getitem__(self, index):
        X = self.inputs[index]
        return X


class Network(nn.Module):
    def __init__(self, all_X_train, arg, random_state=42, X_test=None, Y_test=None):
        torch.manual_seed(random_state)
        np.random.seed(random_state)
        super(Network, self).__init__()
        self.all_X_train = all_X_train
        self.X_test = X_test
        self.Y_test = Y_test
        self.arg = arg

        self.output_criterion = nn.BCELoss()
        self.optimizer = None
        self.best_state_dict = None
        self.best_total_loss = 100000

        # wandb.init(name=f'{self.__class__.__name__}_{self.arg.num_samples}') # will have to rework after getting the dataset

    def _initialize_network(self, input_shape, output_shape):

        self.layer1 = nn.Linear(input_shape, 64)
        self.reconstruct_output = nn.Linear(64, input_shape)

        self.encode_layer = nn.Sequential(
            nn.Linear(input_shape, 64),
            nn.ReLU(),
            nn.Linear(64, num_encoded_features),
            nn.ReLU()
        )

        self.decode_layer = nn.Sequential(
            nn.Linear(num_encoded_features, 64),
            nn.ReLU(),
            nn.Linear(64, input_shape)
        )

        self.output_layer = nn.Sequential(
            nn.Linear(num_encoded_features, 16),
            nn.Linear(16, output_shape),
        )
        self.optimizer = Adam(self.parameters(), lr=0.0001)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer)
        wandb.watch(self)

    def forward(self, inputs):
        encoded_feature = self.encode_layer(inputs)

        # output
        output = torch.sigmoid(self.output_layer(encoded_feature))

        # reconstruction
        reconstruct_output = self.decode_layer(encoded_feature)

        return output, encoded_feature, reconstruct_output

    def freeze_encoder_layer(self):
        for layer in list(self.encode_layer.parameters()):
            layer.requires_grad = False

    def unfreeze_encoder_layer(self):
        for layer in list(self.encode_layer.parameters()):
            layer.requires_grad = True

    def fit(self, limited_inputs, limited_targets):
        # hard code the value 1 for now, we are only predicting 2 values
        self._initialize_network(limited_inputs.shape[1], limited_targets.shape[1])
        self.train(True)
        # make dataset to torch type
        dataset = OnlyXDataset(self.all_X_train)
        # shuffle false because data already shuffled
        data_loader = DataLoader(dataset, batch_size, shuffle=False)
        limited_dataset = TorchDataset(limited_inputs, limited_targets)
        # shuffle false because data already shuffled
        limited_data_loader = DataLoader(limited_dataset, batch_size, shuffle=False)

        # create test dataset
        test_dataset = TorchDataset(self.X_test, self.Y_test)
        test_data_loader = DataLoader(test_dataset, batch_size, shuffle=False)

        for i in range(epoch):
            mean_output_loss = []
            mean_recon_loss = []
            for batch_limit_x, batch_limit_y in limited_data_loader:
                variable_batch_limit_x = Variable(batch_limit_x)
                output, _, _ = self.forward(variable_batch_limit_x)
                output_loss = self.output_criterion(output, batch_limit_y)

                batch_all_x = next(iter(data_loader))
                variable_batch_all_x = Variable(batch_all_x)
                _, _, reconstruction = self.forward(batch_all_x)

                reconstruction_loss = torch.abs(reconstruction - variable_batch_all_x).mean()

                total_loss = output_loss + 0.5 * reconstruction_loss
                self.optimizer.zero_grad()
                total_loss.backward()
                self.optimizer.step()
                mean_output_loss.append(output_loss)
                mean_recon_loss.append(reconstruction_loss)
            wandb.log({'training output loss': sum(mean_output_loss)/len(mean_output_loss),
                       'training reconstruction loss': sum(mean_recon_loss)/len(mean_recon_loss)})
            mean_test_output_loss = []
            mean_test_recon_loss = []
            for x_test, y_test in test_data_loader:
                variable_x_test = Variable(x_test)
                output, _, reconstruction = self.forward(variable_x_test)
                test_output_loss = self.output_criterion(output, y_test)
                test_reconstruction_loss = torch.abs(reconstruction - x_test).mean()

                mean_test_output_loss.append(test_output_loss)
                mean_test_recon_loss.append(test_reconstruction_loss)

            wandb.log({'testing output loss': sum(mean_test_output_loss)/len(mean_test_output_loss),
                       'testing reconstruction loss': sum(mean_test_recon_loss)/len(mean_test_recon_loss)})

            self.scheduler.step(sum(mean_test_output_loss)/len(mean_test_output_loss))

            if sum(mean_test_output_loss)/len(mean_test_output_loss) < self.best_total_loss:
                self.best_state_dict = deepcopy(self.state_dict())
                self.best_total_loss = sum(mean_test_output_loss) / len(mean_test_output_loss)

    def predict(self, inputs):
        self.train(False)
        self.eval()
        self.load_state_dict(self.best_state_dict)

        variable_inputs = Variable(torch.from_numpy(inputs))
        output, _, _ = self.forward(variable_inputs)

        # if sigmoid
        output[output >= 0.5] = 1.
        output[output < 0.5] = 0.

        return output.detach().numpy()

    def score(self, inputs, targets):
        self.train(False)
        self.eval()

        test_dataset = TorchDataset(inputs, targets) # needs to rework when having the finalized data
        data_loader = DataLoader(test_dataset, batch_size, shuffle=False)  # needs to rework when having the finalized data
 
        for batch_x, batch_y in data_loader:
            variable_batch_x = Variable(batch_x)
            variable_batch_y = Variable(batch_y)

            output, reconstruction = self.forward(variable_batch_x)
            output[output >= 0.5] = 1
            output[output < 0.5] = 0
            accuracy = (output.shape[0] - torch.abs(output - variable_batch_y).sum()) / output.shape[0]

            return accuracy