import concurrent.futures
import json
import time as t
from datetime import datetime

from services.aoai_client import CredentialsAOAI, get_promptflow_client
from utils.logger import llmops_logger

from .evaluation import calculate_metrics, sanitize_prediction
from .experiment_output import ExperimentOutput, Replicate

logger = llmops_logger()


def process_flow(
    pf,
    line,
    query_id,
    rule_id,
    variant,
    result_key,
    model_path,
    input_data_path,
    runs,
    retry=5,
):
    inputs = {
        "query": line[f"{query_id}"],
        "truth": line[f"{rule_id}"],
        "rule_id": rule_id,
        "data_file": input_data_path,
    }
    results = []

    while len(results) < runs:
        result = None
        count = 0
        while result is None and count < retry:
            flow_result = pf.test(
                flow=model_path,
                inputs=inputs,
                variant=f"${{classify_with_llm.{variant}}}",
            )

            result = sanitize_prediction(
                flow_result.get("output").get(result_key, None)
            )

            if result is None:
                count += 1
                wait_time = 2**count
                t.sleep(wait_time)

        if count > retry:
            logger.warning(f'Failed to get answer {count} times for: {line["text"]}')

        results.append(result)
    return results


def run_flow(
    dataset_path: str,
    pf_model_path: str,
    input_data_path: str,
    query_id: str,
    rule_id: str,
    aoai_creds: CredentialsAOAI,
    runs: int,
    result_key: str,
    workers: int = 6,
    variant: str = "variant_0",
):
    data_file = open(dataset_path)
    data = json.load(data_file)

    prediction = []
    truth = []

    pf, _ = get_promptflow_client(**(aoai_creds.__dict__))

    logger.info(f"Starting {runs} Runs for {rule_id} with {workers} workers")

    with concurrent.futures.ProcessPoolExecutor(workers) as executor:
        futures = [
            executor.submit(
                process_flow,
                pf,
                line,
                query_id,
                rule_id,
                variant,
                result_key,
                pf_model_path,
                input_data_path,
                runs,
            )
            for line in data
        ]
        concurrent.futures.wait(futures)

        metrics = []
        truth = [line[rule_id] for line in data]
        lines = [line["text"] for line in data]
        predictions = [f.result() for f in futures]

        for replicate_index in range(runs):
            prediction = [p[replicate_index] for p in predictions]
            metrics.append(calculate_metrics(prediction, truth))

        data_file.close()

    return metrics, predictions, truth, lines


def run_experiment(
    dataset_path: str,
    pf_model_path: str,
    input_data_path: str,
    aoai_creds: CredentialsAOAI,
    experiment_name: str = "hypothesis000",
    query_id: str = "text",
    rule_id: str = "r3",
    result_key: str = "violation",
    output_dir: str = "experiment_outputs",
    num_runs: int = 1,
    num_workers: int = 6,
    variant: str = "variant_0",
    output_predictions: bool = True,
    start_time: datetime = datetime.now().strftime("%Y%m%d%H%M"),
) -> ExperimentOutput:
    """Runs an experiment given a dataset, a prediction model, and
    an evaluation model. The models are implemented using promptflow.

    Parameters
    ----------
    dataset_path: str
        Path to dataset.

    pf_model_path: str
        Path to promptflow base model.

    input_data_path: str
        Path to datafile containing prompt input data. Path should be relative to pf_model_path

    aoai_creds: CredentialsAOAI
        Azure OpenAI credentials.

    experiment_name: str
        Name of the experiment for output.

    query_id: str
        Key in the dataset for the query.

    rule_id: str
        Key in the dataset for the truth for each query.

    result_key: str
        Key to the json response from the LLM to use as the prediction.

    num_runs: int
        Number of replicate runs to execute in this experiment.

    num_workers: int = 6,
        Number of workers for flow.

    variant: str = "variant_0",
        Name of the llm variant to run in the PF flow.

    output_dir: str = "experiment_outputs"
        Directory path where metrics will be written.  If
        this directory does not exist, it will be created.

    output_predictions: bool = False
        Flag for serializing predictions to output_dir.

    start_time: datetime
        Sets the starttime for the run so multiple runs will be put in the same directory.


    Return
    ------
    ExperimentOutput
        A dataclass object containing metadata and promptflow Run instances
        from the experiment. Useful attributes of this object include:
        mean_metrics, all_metrics, replicates.
    """

    start = t.time()

    replicates = list()
    # for replicate_idx in range(num_runs):
    metrics, predictions, truth, lines = run_flow(
        dataset_path=dataset_path,
        pf_model_path=pf_model_path,
        input_data_path=input_data_path,
        query_id=query_id,
        rule_id=rule_id,
        result_key=result_key,
        aoai_creds=aoai_creds,
        workers=num_workers,
        runs=num_runs,
        variant=variant,
    )

    for replicate_idx in range(num_runs):
        replicates += [
            Replicate(
                metrics=metrics[replicate_idx],
                predictions=[run[replicate_idx] for run in predictions],
            )
        ]

    elapsed = t.time() - start

    # Build an ExperimentOutput dataclass object to return
    args = {
        "experiment_name": experiment_name,
        "model_name": pf_model_path.split("/")[-1],
        "dataset_ver": dataset_path.split("/")[-1],
        "rule_name": rule_id,
        "num_runs": num_runs,
        "run_time": elapsed,
        "pf_client": None,
        "_start_time": start_time,
        "replicates": replicates,
    }

    exper_out = ExperimentOutput(**args)

    # write outputs to files
    exper_out.to_files(
        metrics_output_dir=output_dir,
        predictions_output=output_predictions,
        truth=truth,
        lines=lines,
    )

    return exper_out
