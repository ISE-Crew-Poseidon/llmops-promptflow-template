"""Module for Azure OpenAI Client and Connection interface"""
import os
import re
from dataclasses import dataclass
from typing import Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import find_dotenv, load_dotenv
from promptflow import PFClient
from promptflow.entities import AzureOpenAIConnection

from src.utils.logger import llmops_logger

logger = llmops_logger()


@dataclass
class CredentialsAOAI:
    azure_openai_api_key: str
    azure_openai_resource_endpoint: str
    conn_name: Optional[str] = "aoai_conn"


def valid_azure_key_vault_url(url):
    pattern = re.compile(
        r"^https:\/\/([a-zA-Z0-9\-]+)\.vault\.(azure|usgovcloudapi)\.net\/?$"
    )
    return pattern.match(url)


def valid_aoai_url(url):
    pattern = re.compile(r"^https:\/\/[a-zA-Z0-9-]+\.openai\.azure\.com\/?$")
    return pattern.match(url)


def get_credentials_aoai():
    error = None
    try:
        load_dotenv(find_dotenv())
        vault_url = os.getenv("KEY_VAULT_URL")
    except IOError:
        raise ValueError("Dotfile containing environment variables not found.")
    if vault_url:
        try:
            if not valid_azure_key_vault_url(vault_url):
                raise ValueError(f"Keyvault URL <{vault_url}> is not valid.")
            # Get Azure Credential
            credential = DefaultAzureCredential()
            secret_aoai_key = os.getenv("KEY_VAULT_AOAI_KEY", "AOAI-KEY")
            secret_aoai_endpoint = os.getenv("KEY_VAULT_AOAI_ENDPOINT", "AOAI-ENDPOINT")
            secret_client = SecretClient(vault_url=vault_url, credential=credential)
            API_KEY = secret_client.get_secret(secret_aoai_key).value
            RESOURCE_ENDPOINT = secret_client.get_secret(secret_aoai_endpoint).value
        except ClientAuthenticationError:
            logger.warning(
                "Unable to read secrets from KeyVault. Try logging in via az login. Falling back onto ENV variables login."
            )
            error = True
        except ValueError:
            logger.warning(
                "Keyvault URL provided is invalid. Falling back onto ENV variables login."
            )
            error = True

    if vault_url is None or error:
        try:
            load_dotenv(find_dotenv())
            API_KEY = os.getenv("AOAI_KEY")
            RESOURCE_ENDPOINT = os.getenv("AOAI_ENDPOINT")
        except IOError:
            raise ValueError(
                "Dotfile containing AOAI_KEY and/or AOAI_ENDPOINT environment variables not found."
            )
    if API_KEY is None or RESOURCE_ENDPOINT is None:
        raise ValueError(
            "AOAI_KEY and/or AOAI_ENDPOINT environment variables not found."
        )
    if not valid_aoai_url(RESOURCE_ENDPOINT):
        raise ValueError(
            f"AOAI_ENDPOINT <{RESOURCE_ENDPOINT}> is not a valid AOAI endpoint."
        )
    return CredentialsAOAI(
        azure_openai_api_key=API_KEY,
        azure_openai_resource_endpoint=RESOURCE_ENDPOINT,
    )


def get_promptflow_client(
    azure_openai_api_key: str,
    azure_openai_resource_endpoint: str,
    conn_name: str = "aoai_conn",
    verbose: bool = False,
):
    """Creates a promptflow client if one already exists and creates one
    otherwise.
    """
    pf = PFClient()

    args = {
        "name": conn_name,
        "api_key": azure_openai_api_key,
        "api_base": azure_openai_resource_endpoint,
        "api_type": "azure",
    }
    if verbose:
        args["stream"] = True

    connection = AzureOpenAIConnection(
        name=conn_name,
        api_key=azure_openai_api_key,
        api_base=azure_openai_resource_endpoint,
        api_type="azure",
    )

    conn = pf.connections.create_or_update(connection)
    if verbose:
        logger.info("Successfully created connection.")

    return pf, conn
