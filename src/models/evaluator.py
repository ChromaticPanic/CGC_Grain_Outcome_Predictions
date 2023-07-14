from sklearn.metrics import precision_score, recall_score, f1_score, roc_curve, log_loss, auc 
from sklearn.model_selection import cross_val_score
import numpy as np


class ModelEvaluator:
    def evaluateModel(self, model, desc, xTrainSet, yTrainSet, xTestSet, yTestSet, numCV=5) -> dict:
        y_train_pred = model.predict(xTrainSet)
        y_pred = model.predict(xTestSet)
        results = {}

        results["desc"] = desc

        calc_accuracies = cross_val_score(model, xTestSet, yTestSet, cv=numCV, scoring="accuracy")
        results["avg_accuracy"] = np.average(calc_accuracies)

        results["r2"] = model.score(xTestSet, yTestSet)
        results["loss"] = log_loss(yTestSet, y_pred)

        results["precision"] = precision_score(yTrainSet, y_train_pred)
        results["recall"] = recall_score(yTrainSet, y_train_pred)
        results["f1"] = f1_score(yTestSet, y_pred)

        fpr, tpr, t = roc_curve(yTestSet, y_pred)
        results["auc"] = auc(fpr, tpr)

        results["importances"] = list(zip(model.feature_importances_, xTestSet.columns))
        results["importances"].sort(reverse=True)

        print(f'[SUCCESS] evaluated {desc}')
        print(f'\tavg_accuracy = {results["avg_accuracy"]}')
        print(f'\tr2 = {results["r2"]}')
        print(f'\tloss = {results["loss"]}')
        print(f'\tprecision = {results["precision"]}')
        print(f'\trecall = {results["recall"]}')
        print(f'\tf1 = {results["f1"]}')
        print(f'\tauc = {results["auc"]}')
        print(f'\tthe top 5 most relevant attributes were:')
        for i in range(5):
            print(f'\t\t{i}{results["importances"][i]}')

        print(f'\tthe top 5 most irrelevant attributes were:')
        for i in range(5):
            print(f'\t\t{i}{results["importances"][len(results["importances"]) - i - 1]}')

        print()

        return results
