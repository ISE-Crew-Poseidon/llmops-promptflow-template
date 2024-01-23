# import json
# from unittest.mock import MagicMock

# import pytest

# from se_req_mve.features.experiment import process_flow


# @pytest.fixture
# def dataset_path():
#     return "src/tests/data/sample_reqs.json"


# @pytest.fixture
# def model_path():
#     return "src/models/sample_hypothesis0"


# @pytest.fixture
# def eval_path():
#     return "src/models/evaluation"


# @pytest.fixture
# def rules_path():
#     return "../../../src/tests/data/sample_rules.json"


# def test_process_flow(dataset_path, model_path, rules_path):
#     data_file = open(dataset_path)
#     data = json.load(data_file)
#     mock_pf = MagicMock()
#     mock_pf.test.return_value = {"output": {"violation": "yes"}}
#     for line in data:
#         output = process_flow(
#             mock_pf,
#             line,
#             "text",
#             "r16",
#             variant="hypothesis001",
#             result_key="violation",
#             model_path=model_path,
#             input_data_path=rules_path,
#             runs=1,
#             retry=5,
#         )
#         print(output)

#     assert mock_pf.test.call_count == 6
