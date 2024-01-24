def is_valid_experiment(data):
    try:
        # Check if 'dataset_path' is a string
        if not isinstance(data.get("dataset_path"), str):
            return False

        # Check if 'pf_model_path' is a string
        if not isinstance(data.get("pf_model_path"), str):
            return False

        # Check if 'input_data_path' is a string
        if not isinstance(data.get("input_data_path"), str):
            return False

        # Check if 'num_runs' is an integer
        if not isinstance(data.get("num_runs"), int):
            return False

        # Check if 'query_id' is a string
        if not isinstance(data.get("query_id"), str):
            return False

        # Check if 'rule_ids' is a list of strings
        if not isinstance(data.get("rule_ids"), list) or not all(
            isinstance(rule_id, str) for rule_id in data.get("rule_ids", [])
        ):
            return False

        # Check if 'result_key' is a string
        if not isinstance(data.get("result_key"), str):
            return False

        # Check if 'variant' is a string
        if not isinstance(data.get("variant"), str):
            return False

        return True
    except TypeError:
        return False
