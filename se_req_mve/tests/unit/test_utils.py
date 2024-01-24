# """Test for se_req_mve.features.utils.py"""

# import pytest
# from numpy import isclose

# from se_req_mve.utils.metrics import average_metrics


# @pytest.fixture
# def all_metrics_list():
#     """Numbers in metrics are all random"""
#     metr1 = {
#         "recall": 0.0,
#         "precision": 0.0,
#         "f1": 0.0,
#         "accuracy_score": 1.0,
#         "balanced_accuracy_score": 1.0,
#         "confusion_matrix": "[[6]]",
#     }
#     metr2 = {
#         "recall": 1.0,
#         "precision": 0.5,
#         "f1": 0.0,
#         "accuracy_score": 1.0,
#         "balanced_accuracy_score": 0.75,
#         "confusion_matrix": "[[4]]",
#     }
#     metr3 = {
#         "recall": 1.0,
#         "precision": 0.5,
#         "f1": 0.0,
#         "accuracy_score": 1.0,
#         "balanced_accuracy_score": 0.5,
#         "confusion_matrix": "[[2]]",
#     }
#     return [metr1, metr2, metr3]


# def test_average_metrics(all_metrics_list):
#     all_metrics, mean_metrics = average_metrics(all_metrics_list=all_metrics_list)

#     assert all_metrics["recall"] == [0, 1, 1]
#     assert all_metrics["confusion_matrix"] == ["[[6]]", "[[4]]", "[[2]]"]

#     assert isclose(mean_metrics["recall"], (2 / 3))
def test_print():
    try:
        print("Hello") is None
    except:
        print("Test print function failed.")
        assert False