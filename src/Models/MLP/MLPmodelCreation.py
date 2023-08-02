import sys
import os
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import sqlalchemy as sq
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_profiling import ProfileReport
from imblearn.over_sampling import RandomOverSampler

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    GridSearchCV,
    KFold,
)
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_curve,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.feature_selection import (
    SelectKBest,
    chi2,
    f_classif,
    mutual_info_classif,
    VarianceThreshold,
)

import tensorflow
from tensorflow import keras
from tensorflow.keras.regularizers import l1, l2, l1_l2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout

import kerastuner as kt
from keras_tuner.tuners import RandomSearch, Hyperband, BayesianOptimization
from sklearn import metrics
from keras import backend as K

from ann_visualizer.visualize import ann_viz
import graphviz

print(os.getcwd())
# sys.path.append("../Shared/")
from Shared.DataService import DataService

sys.path.append("./Datasets/")
# print(os.getcwd())
from DataCreation import getDatasetV1, getDatasetV2, getDatasetV3, getDatasetV4
from DataTestSplit import splitData

# disable GPU
tensorflow.config.set_visible_devices([], "GPU")  # Hide GPU devices
tensorflow.config.set_visible_devices(
    tensorflow.config.list_physical_devices("CPU"), "CPU"
)  # Show CPU devices


def build_model(hp):
    model = Sequential()
    # model.add(Dense(input_dim=X_train.shape[1]))
    for i in range(hp.Int("num_layers", 2, 30)):
        model.add(
            Dense(
                units=hp.Int(
                    "units_" + str(i),
                    min_value=124,  # 32
                    max_value=1748,  # 512
                    step=32,
                ),
                activation=hp.Choice(
                    "act_" + str(i), ["relu", "sigmoid"]
                ),  # , 'tanh', 'elu', 'selu', 'softplus', 'softsign', 'exponential', 'linear'])))
                kernel_regularizer=l1_l2(0.01),
            )
        )

    model.add(Dense(1, activation="sigmoid"))
    model.compile(
        optimizer=Adam(hp.Choice("learning_rate", [1e-2, 1e-3, 1e-4])),
        loss="binary_crossentropy",
        metrics=["accuracy", tensorflow.keras.metrics.AUC(name="auc")],
    )
    return model


# def optimize(build_model, optimizeOn, X_train_rs, y_train_rs, X_val, y_val, epochs):
#     optOn = optimizeOn
#     if optimizeOn == "val_accuracy":
#         print("Optimization on val_accuracy")
#         tuner = BayesianOptimization(
#             build_model,
#             objective="val_accuracy",
#             max_trials=10,
#             overwrite=True,
#             executions_per_trial=2,
#             directory="data/Optimization",
#             project_name="optimization_search",
#         )
#     elif optimizeOn == "val_auc":
#         print("optimizing model on val_auc")
#         tuner = BayesianOptimization(
#             build_model,
#             objective=kt.Objective("val_auc", direction="max"),
#             max_trials=10,
#             overwrite=True,
#             executions_per_trial=2,
#             directory="data/Optimization",
#             project_name="optimization_search",
#         )
#     else:
#         print("Optimization not found")

#     tuner.search(X_train_rs, y_train_rs, epochs=epochs, validation_data=(X_val, y_val))

#     # Method : 1
#     # model = tuner.hypermodel.build(best_hps)
#     # model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test))

#     # Method : 2
#     model = tuner.get_best_models(num_models=1)[0]
#     # model.build(X_train_rs.shape)

#     return model


def optimize(build_model, optimizeOn, X_train_rs, y_train_rs, X_val, y_val, epochs):
    optOn = optimizeOn
    if optimizeOn == "val_accuracy":
        print("Optimization on val_accuracy")
        tuner = BayesianOptimization(
            build_model,
            objective="val_accuracy",
            max_trials=10,
            overwrite=True,
            executions_per_trial=2,
            directory="data/Optimization",
            project_name="optimization_search",
        )
    elif optimizeOn == "val_auc":
        print("optimizing model on val_auc")
        tuner = BayesianOptimization(
            build_model,
            objective=kt.Objective("val_auc", direction="max"),
            max_trials=10,
            overwrite=True,
            executions_per_trial=2,
            directory="data/Optimization",
            project_name="optimization_search",
        )
    else:
        print("Optimization not found")

    # Modify this line to pass hyperparameters 'hp' to the build_model function
    tuner.search(X_train_rs, y_train_rs, epochs=epochs, validation_data=(X_val, y_val))

    # Method : 2
    model = tuner.get_best_models(num_models=1)[0]

    return model


def create_model(X_train_rs, y_train_rs, X_val, y_val, epochs=20):
    model = build_model()
    refined_model = optimize(
        model, "val_auc", X_train_rs, y_train_rs, X_val, y_val, epochs
    )
    return refined_model
