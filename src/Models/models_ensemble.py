from typing import Optional
from imblearn.ensemble import (
    BalancedBaggingClassifier,
    BalancedRandomForestClassifier,
    EasyEnsembleClassifier,
    RUSBoostClassifier,
)
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
    HistGradientBoostingClassifier,
    AdaBoostRegressor,
    BaggingRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
    HistGradientBoostingRegressor,
)


# The goal of ensemble methods is to combine the predictions of several base estimators built with a given learning algorithm in order to improve generalizability / robustness over a single estimator.
# Two families of ensemble methods are usually distinguished:
#     In averaging methods, the driving principle is to build several estimators independently and then to average their predictions. On average, the combined estimator is usually better than any of the single base estimator because its variance is reduced.
#     Examples: Bagging methods, Forests of randomized trees, …
#     By contrast, in boosting methods, base estimators are built sequentially and one tries to reduce the bias of the combined estimator. The motivation is to combine several weak models to produce a powerful ensemble.
#     Examples: AdaBoost, Gradient Tree Boosting, …


def getBalancedClassifier(classifier: int, options: Optional[object] = None) -> object:
    """Get a classifier based on the classifier ID.

    Args:
        classifier (int): The classifier ID.
        options (object, optional): The options for the classifier. Defaults to None.

    Returns:
        object: The classifier.
    """

    if classifier == 0:
        return BalancedBaggingClassifier(options)
    elif classifier == 1:
        return BalancedRandomForestClassifier(options)
    elif classifier == 2:
        return EasyEnsembleClassifier(options)
    elif classifier == 3:
        return RUSBoostClassifier(options)
    else:
        raise ValueError("Invalid classifier ID.")


def getClassifier(classifier: int, options: Optional[object] = None) -> object:
    """Get a classifier based on the classifier ID.

    Args:
        classifier (int): The classifier ID.
        options (object, optional): The options for the classifier. Defaults to None.

    Returns:
        object: The classifier.
    """

    if classifier == 0:
        return AdaBoostClassifier(options)
    elif classifier == 1:
        return BaggingClassifier(options)
    elif classifier == 2:
        return ExtraTreesClassifier(options)
    elif classifier == 3:
        return GradientBoostingClassifier(options)
    elif classifier == 4:
        return RandomForestClassifier(options)
    elif classifier == 5:
        return StackingClassifier(options)
    elif classifier == 6:
        return VotingClassifier(options)
    elif classifier == 7:
        return HistGradientBoostingClassifier(options)
    else:
        raise ValueError("Invalid classifier ID.")
