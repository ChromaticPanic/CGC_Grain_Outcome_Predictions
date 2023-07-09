# ------------------------------------------------------------------
# DecisionTreeVisualizer.py
#
# Remarks: Decision trees are the whitebox of machine learning, therefore, to gain a better understanding, we can use such a system to visualize how features are predicted.
# To run this class a bit of data processing is required, lucky they are a part of sci kit learn:
#   1. Aquire all data into a single data frame
#   2. Impute values (meaning replace NaN or Nulls with an aggregate value)
#   3. Ensure predictors are removed from main data and set aside
#   4. Run setupClassifierTree or setupRegressorTree if needed and check out the cool results!
# ------------------------------------------------------------------
from sklearn.tree import DecisionTreeClassifier  # type: ignore
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import export_graphviz
from subprocess import check_call
from typing import Union
import pandas as pd  # type: ignore
import os


class DecisionTreeVisualizer:
    def __init__(self, max_depth: Union[int, None] = None, random_state: int = 0):
        self.tree = None

        # by default setup to visualize classification
        self.setupClassifierTree(max_depth, random_state)

    def setupClassifierTree(
        self, max_depth: Union[int, None] = None, random_state: int = 0
    ):
        if max_depth:
            self.tree = DecisionTreeClassifier(
                max_depth=max_depth, random_state=random_state
            )
        else:
            self.tree = DecisionTreeClassifier(random_state=random_state)

    def setupRegressorTree(
        self, max_depth: Union[int, None] = None, random_state: int = 0
    ):
        if max_depth:
            self.tree = DecisionTreeRegressor(
                max_depth=max_depth, random_state=random_state
            )
        else:
            self.tree = DecisionTreeRegressor(random_state=random_state)

    def visualize(
        self,
        input: pd.DataFrame,
        predictorCol: str,
        saveName: str = "tree",
        savePath: str = "./",
    ):
        data = input.drop(columns=[predictorCol])
        predictors = input[predictorCol]

        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

            if not self.tree:
                raise ValueError("[ERROR] please setup a tree")

            self.tree.fit(data, predictors)

            class_names_as_string = []
            for label in self.tree.classes_:
                class_names_as_string.append(str(label))

            export_graphviz(
                self.tree,
                out_file="tree.dot",
                feature_names=data.columns.tolist(),
                class_names=class_names_as_string,
                rounded=True,
                filled=True,
            )

            check_call(["dot", "-Tpng", "tree.dot", "-o", f"{savePath}/{saveName}.png"])
            os.remove("tree.dot")
        except Exception as e:
            print(f"[ERROR]: {e}")
            
