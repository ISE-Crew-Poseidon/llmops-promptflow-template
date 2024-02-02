# TROUBLESHOOTING

The initial version of this repository was defined to only execute on the Commercial version of Azure. When attempting to run against a Machine learning workspace that was in Azure Government, we received numerous errors. I am using this document to try to list the errors and what needed to be done to fix them.

## Errors

### Azure Login Error
When attempting to run a github action there was a no subscription found error when logging in. Error message:

```text
Attempting Azure CLI login by using service principal with secret...
Error: No subscriptions found for ***
```

##### Fix

The github action for login assumes an environment of AzureCloud. To update the environment go to the azure login step in the workflow yaml and add the environment field as shown

```yaml
with:
          creds: ${{ secrets.azure_credentials }}
          environment: 'AzureUSGovernment'
```

### AzureCredential Login Error

When attempting to run the github pipeline we received a subscription not found error when it attempted to login via the DefaultAzureCredential

```python
azure.core.exceptions.ResourceNotFoundError: (SubscriptionNotFound) The subscription '50ff9458-6372-4522-8227-327043deaef5' could not be found.
Code: SubscriptionNotFound
Message: The subscription '50ff9458-6372-4522-8227-327043deaef5' could not be found.
```

#### Fix

Update DefaultAzureCredential to include the authority `DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)`, add kwargs to the MLClient creation to add cloud setting `{"cloud": "AzureUSGovernment"}`, and add environment variable `AZUREML_CLOUD_ENV_NAME: "AzureUSGovernment"`. The kwargs may not be necessary because it should be handled by the environment variable, but did both.

### Invalid Token Error

When submitting a new run via promptflow we started getting an Invalid Token error. Error:

```python
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/_restclient/flow_service_caller.py", line 62, in wrapper
    return func(self, *args, **kwargs)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/_restclient/flow_service_caller.py", line 501, in create_flow_session
    map_error(status_code=response.status_code, response=response, error_map=error_map)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/azure/core/exceptions.py", line 165, in map_error
    raise error
azure.core.exceptions.ClientAuthenticationError: (UserError) Invalid token
Code: UserError
Message: Invalid token

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/runpy.py", line 197, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/home/runner/work/llmops-promptflow-template/llmops-promptflow-template/llmops/common/prompt_pipeline.py", line 421, in <module>
    main()
  File "/home/runner/work/llmops-promptflow-template/llmops-promptflow-template/llmops/common/prompt_pipeline.py", line 408, in main
    prepare_and_execute(
  File "/home/runner/work/llmops-promptflow-template/llmops-promptflow-template/llmops/common/prompt_pipeline.py", line 268, in prepare_and_execute
    pipeline_job = pf.runs.create_or_update(run, stream=True)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/_sdk/_telemetry/activity.py", line 175, in wrapper
    return f(self, *args, **kwargs)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 236, in create_or_update
    rest_obj = self._resolve_dependencies_in_parallel(run=run, runtime=kwargs.get("runtime"), reset=reset)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 956, in _resolve_dependencies_in_parallel
    task_results = [task.result() for task in tasks]
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 956, in <listcomp>
    task_results = [task.result() for task in tasks]
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/concurrent/futures/_base.py", line 439, in result
    return self.__get_result()
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/concurrent/futures/_base.py", line 391, in __get_result
    raise self._exception
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 942, in _resolve_runtime
    runtime = self._resolve_automatic_runtime(run=run, session_id=session_id, reset=reset)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 932, in _resolve_automatic_runtime
    self._resolve_session(run=run, session_id=session_id, reset=reset)
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/operations/_run_operations.py", line 917, in _resolve_session
    self._service_caller.create_flow_session(
  File "/opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/promptflow/azure/_restclient/flow_service_caller.py", line 64, in wrapper
    raise FlowRequestException(
promptflow.azure._restclient.flow_service_caller.FlowRequestException: Calling create_flow_session failed with request id: 04c0402d-d963-4bd0-b8b1-0ce8bef2da3e 
Status code: 401 
Reason: Invalid token 
Error message: (UserError) Invalid token
Code: UserError
Message: Invalid token 

Error: Process completed with exit code 1.
```

#### Fix
<s> The authentication for the promptflow client has the value of "http://management.azure.com" hardcoded for creating an Authentication token. So the endpoint will be correctly pointed to US government, but the auth token created is for Azure Commercial leading to the 401 error. We created a virtual environment and manually changed the hard coded values to point to management.usgovcloudapi.net. </s> This has been fixed in Promptflow versions >1.4.0

### Automatic Runtime Error

When running a job using an Automatic Runtime I received a CredentialNotFound error. This is because an automatic runtime does not assign a ManagedIdentity by default. There does not seem to be a way to assign an identity using the promptflow methods.

#### Fix

This has been fixed in later versions of the Promptflow Runtime. Try running version > 20240116.v1

### Managed Runtime Error

When running a custom runtime upon posting a job we are seeing a SubscriptionNotFound error like below.

```python
Traceback (most recent call last):
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/data.py", line 232, in prepare_data
    return _download_aml_uri(uri, destination, credential, runtime_config)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/data.py", line 195, in _download_aml_uri
    return download_artifact_from_aml_uri(uri, destination, ml_client.datastores)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/_artifacts/_artifact_utilities.py", line 339, in download_artifact_from_aml_uri
    return download_artifact(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/_artifacts/_artifact_utilities.py", line 290, in download_artifact
    datastore_info = get_datastore_info(datastore_operation, datastore_name)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/_artifacts/_artifact_utilities.py", line 88, in get_datastore_info
    datastore = operations.get(name, include_secrets=credential is None)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/_telemetry/activity.py", line 275, in wrapper
    return f(*args, **kwargs)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/operations/_datastore_operations.py", line 140, in get
    datastore_resource = self._operation.get(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/core/tracing/decorator.py", line 78, in wrapper_use_tracer
    return func(*args, **kwargs)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/ai/ml/_restclient/v2023_04_01_preview/operations/_datastores_operations.py", line 512, in get
    map_error(status_code=response.status_code, response=response, error_map=error_map)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azure/core/exceptions.py", line 164, in map_error
    raise error
azure.core.exceptions.ResourceNotFoundError: (SubscriptionNotFound) The subscription '50ff9458-6372-4522-8227-327043deaef5' could not be found.
Code: SubscriptionNotFound
Message: The subscription '50ff9458-6372-4522-8227-327043deaef5' could not be found.
```

#### Fix

The issue is that the credential is for Azure Gov, but the rest client found under MLClient is attempting to figure out which cloud it should point to and defaults to AzureCloud. When calling that cloud with a Gov subscription it fails. The fix is around the environment variable AZUREML_CURRENT_CLOUD. When you create the Custom Runtime you should add an environment variable of AZUREML_CURRENT_CLOUD=AzureUSGovernment. I found inconsistent results on updating an existing runtime so how I did it was on a managed compute instance, I created a custom application with these settings, please update to point to your environment

```text
Create custom application
image: mcr.microsoft.com/azureml/promptflow/promptflow-runtime:20231218.v2
env vars:
AZURE_CLIENT_ID : <client-id of your managed-identity>
AZURE_RESOURCE_MANAGER : https://management.usgovcloudapi.net/
AZUREML_CURRENT_CLOUD : AzureUSGovernment
PRT_CONFIG_OVERRIDE : storage.storage_account=ngcengreqsmve,deployment.subscription_id=50ff9458-6372-4522-8227-327043deaef5,deployment.resource_group=ngc-eng-reqs-mve,deployment.workspace_name=ngcengreqsmve,deployment.endpoint_name=mc-compute,deployment.deployment_name=mc-runtime-20240111195035670,deployment.mt_service_endpoint=https://usgovvirginia.api.ml.azure.us,deployment.runtime_name=mc-runtime

bind mounts /var/run/docker.sock : /var/run/docker.sock
```

This was able to allow the job to actually start, but it would hang on NotStarted.

### Run Not Started Error

When trying to execute a run via the UI or submitting to the custom runtime the job would sit permanently as not started. When logged onto the terminal of the runtime and tailing the docker logs using `docker logs -f <runtime name>` I was able to see the following error:

```python
Traceback (most recent call last):
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/utils/_utils.py", line 214, in multi_processing_exception_wrapper
    yield
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/runtime.py", line 247, in execute_flow_request_multiprocessing_impl
    result = execute_flow_func(config, request)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/runtime.py", line 657, in execute_bulk_run_request
    run_storage = config.get_run_storage(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/runtime_config.py", line 349, in get_run_storage
    return self.get_azure_ml_run_storage_v2(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/runtime_config.py", line 416, in get_azure_ml_run_storage_v2
    return AzureMLRunStorageV2(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/storage/azureml_run_storage_v2.py", line 133, in __init__
    self._write_flow_artifacts_meta_to_blob()
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/storage/azureml_run_storage_v2.py", line 326, in _write_flow_artifacts_meta_to_blob
    self.upload_blob(blob_client, json.dumps(meta), overwrite=True)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/utils/retry_utils.py", line 39, in f_retry
    return f(*args, **kwargs)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/storage/azureml_run_storage_v2.py", line 79, in wrapper
    raise AzureStorageOperationError(
promptflow.runtime._errors.AzureStorageOperationError: Failed to upload run info to blob. Original error: <urllib3.connection.HTTPSConnection object at 0x7fed5a692dc0>: Failed to resolve 'ngcengreqsmve.blob.core.windows.net' ([Errno -2] Name or service not known)
```

What is happening is that the job is starting correctly and then when it attempts to update the status of the job it is using a hard coded AzureCloud endpoint which fails. This causes the job to fail, but it also means the status never updates on the job which is why it stays in the Not Started status

#### Fix

<s> Looking inside the docker container you can find the promptflow runtime code at `/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/storage/azureml_run_storage_v2.py` which has the storage accout BlobServiceClient hardcoded to 

```python
blob_url = f"https://{storage_account_name}.blob.core.windows.net"
```

Log into the docker container with `docker exec -it <runtime> /bin/bash`. Then execute the following command `grep -rl 'blob.core.windows.net' /azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/storage/| xargs sed -i 's/blob.core.windows.net/blob.core.usgovcloudapi.net/g'` </s> 
This has been fixed in version 20240116.v1 of the Promptflow runtime

### 403 error in tracking mlflow

When performing a run we are getting a 403 when attempting to track the run. This is the error:

```python
Traceback (most recent call last):
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/promptflow/runtime/utils/mlflow_helper.py", line 100, in start_run
    mlflow.start_run(run_id=run_id)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/mlflow/tracking/fluent.py", line 334, in start_run
    _get_store().update_run_info(
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/azureml/mlflow/_store/tracking/store.py", line 52, in update_run_info
    return super(AzureMLRestStore, self).update_run_info(run_id, *args, **kwargs)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/mlflow/store/tracking/rest_store.py", line 151, in update_run_info
    response_proto = self._call_endpoint(UpdateRun, req_body)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/mlflow/store/tracking/rest_store.py", line 59, in _call_endpoint
    return call_endpoint(self.get_host_creds(), endpoint, method, json_body, response_proto)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/mlflow/utils/rest_utils.py", line 219, in call_endpoint
    response = verify_rest_response(response, endpoint)
  File "/azureml-envs/prompt-flow/runtime/lib/python3.9/site-packages/mlflow/utils/rest_utils.py", line 157, in verify_rest_response
    raise MlflowException(
mlflow.exceptions.MlflowException: API request to endpoint /api/2.0/mlflow/runs/update failed with error code 403 != 200. Response body: ''
```

#### Fix

The issue is with authentication. The managed identity for the compute I am using does not have AzureML Data Scientist rights, add that role for the workspace and try again.

### AOAI Connection Not Found

The promptflow yaml files expect to have a connection setup in AML called AOAI. Currently when setting up a connection in the UI you must point to an OpenAI endpoint in the same environment. Since Azure OpenAI is currently only available in Azure Commercial you cannot create a connection via the UI

#### Fix

Create the connection via the API. Sample code:

```python
import requests
import json

aoai_connection_name = "aoai_conn2"  # Change this to add a new connection
subscription_id = SUBSCRIPTION_ID
resource_group = RESOURCE_GROUP
workspace_name = AML_WORKSPACE_NAME
aoai_api_base = AOAI_CREDS.azure_openai_resource_endpoint
aoai_api_key = AOAI_CREDS.azure_openai_api_key
aoai_api_type = "azure"
aoai_api_version = "2023-12-01-preview"

url = (
    f"https://management.usgovcloudapi.net/subscriptions/{subscription_id}/"
    f"resourcegroups/{resource_group}/providers/Microsoft.MachineLearningServices/"
    f"workspaces/{workspace_name}/connections/{aoai_connection_name}"
    f"?api-version=2023-04-01-preview"
)
token = credential.get_token("https://management.usgovcloudapi.net/.default").token
header = {
    "Authorization": f"Bearer {token}",
    "content-type": "application/json",
}

data = json.dumps(
    {
        "properties": {
            "category": "AzureOpenAI",
            "target": aoai_api_base,
            "authType": "ApiKey",
            "credentials": {
                "key": aoai_api_key,
            },
            "metadata": {
                "ApiType": aoai_api_type,
                "ApiVersion": aoai_api_version,
            },
        }
    }
)

with requests.Session() as session:
    response = session.put(url, data=data, headers=header)
    # Raise an exception if the response contains an HTTP error status code
    response.raise_for_status()

print(response.json())
```

### NotStarted Error on Created Runtime
When the promptflow runtime issues were solved I was still getting an issue where on runtimes created by the Service Principal I was unable to get a run to start. Since I did not have terminal access to the compute I was unable to see anything other than UserError.

#### Fix
I created a new Compute instance with SSH access, this allowed me to log into the terminal remotely. The flag for this is under `az ml compute create` is `--ssh-public-access-enabled true` and `--ssh-key-value` with a public key value. Once logged into the box do a `docker ps` to see the name of the runtime and run `docker logs -f <runtime name>` to follow the logs of your runtime.

Once doing this I discovered the issues was the Managed Identity of the runtime did not have Storage Blob Data Contributor access to the Storage Account that backed the Azure ML Workspace. Once adding that role the jobs started successfully.