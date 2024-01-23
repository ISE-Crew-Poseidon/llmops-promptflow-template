from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml._azure_environments import _get_default_cloud_name, EndpointURLS, _get_cloud, AzureEnvironments
from promptflow.azure import PFClient

def get_credential():
    cloud_name = _get_default_cloud_name()
    if cloud_name != AzureEnvironments.ENV_DEFAULT:
        cloud = _get_cloud(cloud=cloud_name)
        authority = cloud.get(EndpointURLS.ACTIVE_DIRECTORY_ENDPOINT)
        credential = DefaultAzureCredential(authority=authority, exclude_shared_token_cache_credential=True)
    else:
        credential = DefaultAzureCredential()
        
    return credential

def get_ml_client(subscription_id, resource_group_name, workspace_name):
    ml_client = MLClient(
        get_credential(),
        subscription_id,
        resource_group_name,
        workspace_name
    )

    return ml_client

def get_pf_client(subscription_id, resource_group_name, workspace_name):
    pf = PFClient(
        get_credential(),
        subscription_id,
        resource_group_name,
        workspace_name
    )

    return pf