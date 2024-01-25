from typing import List

from promptflow import log_metric, tool
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


@tool
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
