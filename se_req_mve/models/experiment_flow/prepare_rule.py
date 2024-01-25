import json

from promptflow import tool


# flake8: noqa
@tool
def prepare_rule_data(data_file: str, rule_id: str) -> str:
    """Static rule data.  Should output raw text.
    Parameters
    -------
    rule_id: str
        ID of the rule, case-sensitive. e.g., "r3"

    Output
    ------
    str
        Text representation of rule data. This will be passed into
        the LLM prompt as rule context.

    """
    with open(data_file, "r") as f:
        rules = json.load(f)

        rule_dict = [my_rule for my_rule in rules if my_rule["id"] == rule_id][0]
        return rule_dict
