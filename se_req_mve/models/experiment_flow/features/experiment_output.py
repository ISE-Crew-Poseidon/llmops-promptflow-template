import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from pandas import DataFrame
from promptflow import PFClient

from ..utils.metrics import average_metrics


@dataclass
class Replicate:
    """Contains data for a replicate run

    metrics: Dict[str, float]
        Metrics from the replciate run.

    predictions: [bool]
        Prediction outputs

    """

    metrics: Dict[str, float]
    predictions: [bool]

    def _build_output_df(self, truth, lines) -> DataFrame:
        """Builds a dataframe of predictions."""

        df = DataFrame()
        df["line"] = lines
        df["prediction"] = self.predictions
        df["truth"] = truth
        return df


@dataclass
class ExperimentOutput:
    """Outputs from an experiment

    Parameters:
    ----------
    model_name: str
        The name of the model usually given by its flow directory name.

    dataset_ver: str
        The filename of the dataset.

    rule_name: str
        Name of the rule being tested in the experiment.

    num_runs: int
        Number of experiment replicates.

    run_time: float
        Runtime in seconds

    pf_client: PFClient
        Promptflow client object.

    replicates: List[Replicate]
        A list of replicates composing this experiment

    mean_metrics: Dict[str, List] = None
        A dictionary of average metrics over all replciate runs.

    all_metrics: Dict[str, List] = None
        A dictionary of all metrics from the experiment replicate runs.

    metrics_file: Optional[str] = None
        Output file name that stores experiment metrics and metadata.

    predictions_dir: Optional[str] = None
        Output directory that stores experiment predictions.

    """

    experiment_name: str
    model_name: str
    dataset_ver: str
    rule_name: str
    num_runs: int
    run_time: float
    pf_client: PFClient
    replicates: List[Replicate]
    _start_time: datetime = datetime.now().strftime("%Y%m%d%H%M")
    mean_metrics: Dict[str, float] = None
    all_metrics: Dict[str, List[float]] = None
    metrics_file: Optional[str] = None
    predictions_dir: Optional[str] = None

    def __post_init__(self):
        """Parse replicates to build self.all_metrics and self.mean_metrics
        attributes.
        """
        all_metrics_list = [r.metrics for r in self.replicates]

        self.all_metrics, self.mean_metrics = average_metrics(
            all_metrics_list=all_metrics_list
        )

    def to_files(
        self,
        metrics_output_dir: str = "experiment_output",
        predictions_output: bool = False,
        truth: [bool] = [],
        lines: [str] = [],
    ):
        """Writes metrics and/or predictions to files under the input directory path
        specified by `metrics_output_dir`. If predictions_output is set to False, it
        will not be serialized to files.

        """
        output_dir_for_exprmt = (
            f"{metrics_output_dir}/results/{self.experiment_name}/{self.rule_name}"
        )
        os.makedirs(output_dir_for_exprmt, exist_ok=True)

        if predictions_output:
            self.predictions_dir = f"{output_dir_for_exprmt}/runs"
            os.makedirs(self.predictions_dir, exist_ok=True)
            self._predictions_to_file(truth, lines)

        if metrics_output_dir:
            self.metrics_file = f"{output_dir_for_exprmt}/metrics.json"
            self._metrics_to_file()

    def _metrics_to_file(self):
        """Write metadata and metrics to self.metrics_file.
        The list of attributes that are serialized are predefined.

        Metrics are outputted to `{metrics_output_dir}/{model_name}{datetime}/metrics.json`.
        Predictions are outputted to `{metrics_output_dir}/{model_name}{datetime}/runs/`.
        """
        with open(self.metrics_file, "w") as f:
            json.dump(
                {
                    k: self.__dict__[k]
                    for k in [
                        "model_name",
                        "rule_name",
                        "dataset_ver",
                        "mean_metrics",
                        "all_metrics",
                        "run_time",
                        "num_runs",
                        "predictions_dir",
                    ]
                },
                f,
            )

    def _predictions_to_file(self, truth, lines):
        """Collect base_run outputs and write to JSONL files."""
        for idx, replicate in enumerate(self.replicates):
            df = replicate._build_output_df(truth, lines)
            df.to_json(
                f"{self.predictions_dir}/replicate_{idx:03}.jsonl",
                orient="records",
                lines=True,
            )
