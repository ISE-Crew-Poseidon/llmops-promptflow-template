"""
This module executes experiment jobs/bulk-runs using standard flows.

Args:
--subscription_id: The Azure subscription ID.
This argument is required for identifying the Azure subscription.
--data_purpose: The data identified by its purpose.
This argument is required to specify the purpose of the data.
--flow_to_execute: The name of the flow use case.
This argument is required to specify the name of the flow for execution.
--env_name: The environment name for execution and deployment.
This argument is required to specify the environment (dev, test, prod)
for execution or deployment.
"""

import argparse
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
import json

from llmops.common.logger import llmops_logger
from llmops.common.utils.get_clients import get_ml_client

logger = llmops_logger("register_data_asset")

parser = argparse.ArgumentParser("register data assets")
parser.add_argument(
    "--subscription_id", type=str, help="Azure subscription id", required=True
)
parser.add_argument(
    "--data_purpose",
    type=str,
    help="data to be registered identified by purpose",
    required=True,
)
parser.add_argument(
    "--flow_to_execute", type=str, help="data config file path", required=True
)
parser.add_argument(
    "--env_name",
    type=str,
    help="environment name (e.g. dev, test, prod)",
    required=True,
)

args = parser.parse_args()

environment_name = args.env_name
main_config = open(f"{args.flow_to_execute}/llmops_config.json")
config = json.load(main_config)

for obj in config["envs"]:
    if obj.get("ENV_NAME") == environment_name:
        model_config = obj
        break

data_config_path = f"{args.flow_to_execute}/configs/data_config.json"
resource_group_name = model_config["RESOURCE_GROUP_NAME"]
workspace_name = model_config["WORKSPACE_NAME"]
data_purpose = args.data_purpose


ml_client = get_ml_client(args.subscription_id, resource_group_name, workspace_name)

config_file = open(data_config_path)
data_config = json.load(config_file)

for elem in data_config["datasets"]:
    if "DATA_PURPOSE" in elem and "ENV_NAME" in elem:
        if (
            data_purpose == elem["DATA_PURPOSE"]
            and environment_name == elem["ENV_NAME"]
        ):
            data_path = f"{args.flow_to_execute}/{elem['DATA_PATH']}"
            dataset_desc = elem["DATASET_DESC"]
            dataset_name = elem["DATASET_NAME"]

            aml_dataset = Data(
                path=data_path,
                type=AssetTypes.URI_FILE,
                description=dataset_desc,
                name=dataset_name,
            )
            ml_client.data.create_or_update(aml_dataset)

            aml_dataset_unlabeled = ml_client.data.get(
                name=dataset_name, label="latest"
            )

            logger.info(aml_dataset_unlabeled.latest_version)
            logger.info(aml_dataset_unlabeled.id)
