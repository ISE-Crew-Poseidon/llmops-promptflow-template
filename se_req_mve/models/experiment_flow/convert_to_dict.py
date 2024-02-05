import json

from promptflow import tool

from utils.logger import llmops_logger

logger = llmops_logger()


@tool
def convert_to_dict(input_str: str) -> dict:
    """Converts the raw text output from the LLM into a dictionary."""
    try:
        response = json.loads(input_str)
        assert "violation" in response
        response["violation"] = response["violation"].lower() in [
            "yes",
            "correct",
            "true",
        ]
        return response

    except Exception as e:
        logger.error("The input is not valid, error: {}".format(e))
        return {"violation": None, "reason": "Failed to parse LLM output."}