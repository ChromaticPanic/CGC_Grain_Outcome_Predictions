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


class ModelEvaluator:
    def evaluateClassification(
        self,
        model,
        desc,
        xTrainSet,
        yTrainSet,
        xTestSet,
        yTestSet,
        saveFactorsLoc=None,
        hasFeatImportance=True,
        numCV=5,
    ) -> dict:
        y_train_pred = model.predict(xTrainSet)
        y_pred = model.predict(xTestSet)
        results = {}

        results["desc"] = desc

        calc_accuracies = cross_val_score(
            model, xTestSet, yTestSet, cv=numCV, scoring="neg_mean_squared_error"
        )
        results["avg_accuracy"] = np.average(calc_accuracies)

        results["r2"] = model.score(xTestSet, yTestSet)
        results["loss"] = log_loss(yTestSet, y_pred)

        results["precision"] = precision_score(yTrainSet, y_train_pred)
        results["recall"] = recall_score(yTrainSet, y_train_pred)
        results["f1"] = f1_score(yTestSet, y_pred)

        fpr, tpr, t = roc_curve(yTestSet, y_pred)
        results["auc"] = auc(fpr, tpr)

        if hasFeatImportance:
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

    def evaluateRegression(
        self,
        model,
        desc,
        xTrainSet,
        yTrainSet,
        xTestSet,
        yTestSet,
        saveFactorsLoc=None,
        hasFeatImportance=True,
        numCV=5,
    ) -> dict:
        results = {}

        results["desc"] = desc

        calc_accuracies = cross_val_score(
            model, xTestSet, yTestSet, cv=numCV, scoring="neg_mean_squared_error"
        )
        results["avg_accuracy"] = np.average(calc_accuracies)

        results["r2"] = model.score(xTestSet, yTestSet)

        if hasFeatImportance:
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

    def __saveRelevantFeatures(self, features, saveFactorsLoc):
        if saveFactorsLoc != None:
            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))

                with open(saveFactorsLoc, "a") as file:
                    for i in range(10):
                        file.write(f"{features[i][1]},")
            except:
                pass

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
