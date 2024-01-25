from promptflow import tool


@tool
def sanitize_prediction(prediction_str: str) -> bool:
    """Boolean cast on input string."""
    if prediction_str:
        return prediction_str.lower() in ["yes", "correct", "true"]
    else:
        return None
