from typing import List

from promptflow import log_metric
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.utils.logger import llmops_logger

logger = llmops_logger()


def calculate_metrics(predictions: List, truth: List) -> dict:
    """Computes metrics from pred and truth lists."""

    truth = [bool(t) for t in truth]

    metrics = {
        "recall": recall_score(y_pred=predictions, y_true=truth, zero_division=0),
        "precision": precision_score(y_pred=predictions, y_true=truth, zero_division=0),
        "f1": f1_score(y_pred=predictions, y_true=truth, zero_division=0),
        "accuracy_score": accuracy_score(y_pred=predictions, y_true=truth),
        "balanced_accuracy_score": balanced_accuracy_score(
            y_pred=predictions, y_true=truth
        ),
        "confusion_matrix": str(
            confusion_matrix(y_pred=predictions, y_true=truth)
        ).replace("\n", ","),
    }
    for metric_name, val in metrics.items():
        log_metric(metric_name, val)
    return metrics


def sanitize_prediction(prediction_str: str) -> bool:
    """Boolean cast on input string."""
    if isinstance(prediction_str, str):
        return prediction_str.lower() in ["yes", "correct", "true"]
    elif isinstance(prediction_str, bool):
        return prediction_str
    else:
        logger.warning(f"Got None for: {prediction_str}")
        return None
