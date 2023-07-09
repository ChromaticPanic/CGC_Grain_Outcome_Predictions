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
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import export_graphviz
from subprocess import check_call
import os

class DecisionTreeVisualizer:
    def __init__(self, max_depth=None, random_state=0) -> None:
        self.tree = None

        self.setupClassifierTree(max_depth, random_state)   # by default setup to visualize classification


    def setupClassifierTree(self, max_depth=None, random_state=0):
        if max_depth:
            self.tree = DecisionTreeClassifier(max_depth=max_depth, random_state=random_state)
        else:
            self.tree = DecisionTreeClassifier(random_state=random_state)

    def setupRegressorTree(self, max_depth=None, random_state=0):
        if max_depth:
            self.tree = DecisionTreeRegressor(max_depth=max_depth, random_state=random_state)
        else:
            self.tree = DecisionTreeRegressor(random_state=random_state)


    def visualize(self, input, predictorCol, saveName='tree', savePath='./'):
        data = input.drop(columns=[predictorCol])
        predictors = input[predictorCol]
    
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
                filled=True
            )

            check_call(['dot','-Tpng','tree.dot','-o', f'{savePath}/{saveName}.png'])
            os.remove('tree.dot')
        except Exception as e:
            print(f'[ERROR]: {e}')