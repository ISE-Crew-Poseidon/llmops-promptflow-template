from promptflow import tool


@tool
def score(prediction: bool, truth: bool) -> bool:
    """Returns if prediction was correct as bool"""
    return prediction == truth
