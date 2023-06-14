import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC, LinearSVC
# from sklearn.metrics import f1_score


model_dict = {
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
    "decision_tree": DecisionTreeClassifier,
    "gradient_boost": GradientBoostingClassifier,
    "svc": SVC,
    "linear_svc": LinearSVC,
}

def model_initializer(all_X_train, arg, model_type, random_state=42, X_test=None, Y_test=None):
    
    # This will be used later when we actually import the autoencoder model
    # if "autoencoder" in model_type: 
    #     model_selected = model_dict[model_type](all_X_train, arg, random_state=random_state, X_test=X_test, Y_test=Y_test)
    # else:
    model_selected = model_dict[model_type](random_state=random_state)
    return model_selected

# This is a function supposed to run the model on k folds of the dataset and find the mean f_1 score
# def evaluate_model(dataset, arg, model_name):

# Compare all the models
# def compare_all_models(arg):