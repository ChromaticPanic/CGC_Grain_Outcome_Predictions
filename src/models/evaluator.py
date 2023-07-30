#-----------------------------------------------------------
#evaluator.py
# The purpose of the provided code is to define a class which contains methods for evaluating machine learning models for both classification and regression tasks.
# The class provides functions to calculate various evaluation metrics for the models, such as accuracy, R-squared, precision, recall, F1 score, and area under the receiver operating characteristic curve (AUC-ROC). 
#
#-----------------------------------------------------------

from sklearn.model_selection import cross_val_score  # type: ignore
from sklearn.metrics import precision_score  # type: ignore
from sklearn.metrics import recall_score  # type: ignore
from sklearn.metrics import f1_score  # type: ignore
from sklearn.metrics import roc_curve  # type: ignore
from sklearn.metrics import log_loss  # type: ignore
from sklearn.metrics import auc  # type: ignore
from collections import Counter
from typing import Dict
import numpy as np
import os

# Purpose:
# It intends to evaluate the performance of a given classification model using various metrics. 
# The method takes a classification model, a description of the evaluation, training and testing datasets, and optional parameters.

class ModelEvaluator:
    def evaluateClassification(
        self,
        model,                 # The classification model to be evaluated
        desc,                  # A description of the evaluation
        xTrainSet,             # Training dataset features
        yTrainSet,             # Training dataset labels
        xTestSet,              # Testing dataset features
        yTestSet,              # Testing dataset labels
        saveFactorsLoc=None,   # Optional: Path to save the feature importances
        hasFeatImportance=True, # Optional: Flag to calculate feature importances
        numCV=5,                # Optional: Number of cross-validation folds
    ) -> dict:                 # Returns a dictionary containing the evaluation results

        y_train_pred = model.predict(xTrainSet)
        y_pred = model.predict(xTestSet)
        results = {}

        results["desc"] = desc

        # Perform cross-validation to calculate the average negative mean squared error
        calc_accuracies = cross_val_score(
            model, xTestSet, yTestSet, cv=numCV, scoring="neg_mean_squared_error"
        )
        results["avg_accuracy"] = np.average(calc_accuracies) # Calculate the average accuracy

        results["r2"] = model.score(xTestSet, yTestSet) # Calculate the R-squared score
        results["loss"] = log_loss(yTestSet, y_pred)  # Calculate the log loss

        # Calculate precision, recall, and F1 score on the training and testing sets
        results["precision"] = precision_score(yTrainSet, y_train_pred)
        results["recall"] = recall_score(yTrainSet, y_train_pred)
        results["f1"] = f1_score(yTestSet, y_pred)

        # Calculate the area under the ROC curve (AUC)
        fpr, tpr, t = roc_curve(yTestSet, y_pred)
        results["auc"] = auc(fpr, tpr)

        if hasFeatImportance:
            # If feature importance calculation is required
            # Calculate feature importances and save them in the results
            results["importances"] = list(
                zip(model.feature_importances_, xTestSet.columns)
            )
            results["importances"].sort(reverse=True)

            self.__saveRelevantFeatures(results["importances"], saveFactorsLoc)

        print(f"[SUCCESS] evaluated {desc}")
        print(f'\tavg_accuracy = {results["avg_accuracy"]}')
        print(f'\tr2 = {results["r2"]}')
        print(f'\tloss = {results["loss"]}')
        print(f'\tprecision = {results["precision"]}')
        print(f'\trecall = {results["recall"]}')
        print(f'\tf1 = {results["f1"]}')
        print(f'\tauc = {results["auc"]}')

        if hasFeatImportance:
            print(f"\tthe top 10 most relevant attributes were:")

            for i in range(10):
                print(f'\t\t{i}{results["importances"][i]}')

        print()

        return results
    
    # Purpose:
    #  evaluate the performance of a given regression model using cross-validation and provide various metrics for assessment. 
    #  It takes a regression model, a description of the evaluation, training and testing datasets, and optional parameters. 

    def evaluateRegression(
            self,
            model,                 # The regression model to be evaluated
            desc,                  # A description of the evaluation
            xTrainSet,             # Training dataset features
            yTrainSet,             # Training dataset labels
            xTestSet,              # Testing dataset features
            yTestSet,              # Testing dataset labels
            saveFactorsLoc=None,   # Optional: Path to save the feature importances
            hasFeatImportance=True, # Optional: Flag to calculate feature importances
            numCV=5,                # Optional: Number of cross-validation folds
    ) -> dict:
        results = {}

        results["desc"] = desc
        # Perform cross-validation to calculate the average negative mean squared error
        calc_accuracies = cross_val_score(
            model, xTestSet, yTestSet, cv=numCV, scoring="neg_mean_squared_error"
        )
        results["avg_accuracy"] = np.average(calc_accuracies) # Calculate the average accuracy

        results["r2"] = model.score(xTestSet, yTestSet)  # Calculate the R-squared score

        if hasFeatImportance:
            # If feature importance calculation is required
            # Calculate feature importances and save them in the results
            results["importances"] = list(
                zip(model.feature_importances_, xTestSet.columns)
            )
            results["importances"].sort(reverse=True)

            self.__saveRelevantFeatures(results["importances"], saveFactorsLoc)

        print(f"[SUCCESS] evaluated {desc}")
        print(f'\tavg_accuracy = {results["avg_accuracy"]}')
        print(f'\tr2 = {results["r2"]}')

        if hasFeatImportance:
            print(f"\tthe top 10 most relevant attributes were:")

            for i in range(10):
                print(f'\t\t{i}{results["importances"][i]}')

        print()

        return results

    # Purpose :
    # It intends to save the top relevant features. 
    def __saveRelevantFeatures(self, features, saveFactorsLoc):
        if saveFactorsLoc != None:
            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))

                with open(saveFactorsLoc, "a") as file:
                    for i in range(10):
                        file.write(f"{features[i][1]},")
            except:
                pass
    # Purpose :
    # It intends to read the top relevant features. 
    def readRelevantFeatures(self, saveFactorsLoc) -> dict:
        dist: Dict[str, int] = {}

        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            with open(saveFactorsLoc, "r") as file:
                content = file.read()

                allFeatures = content.split(",")
                dist = Counter(allFeatures)
        except:
            pass

        return dist
