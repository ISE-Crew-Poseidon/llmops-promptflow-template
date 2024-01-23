"""violin distribution plots for metrics"""
import glob
import json
import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils.logger import llmops_logger

logger = llmops_logger()


def _get_df_for_all_runs(
    dataset_folder: str,
    rule_id: str = "r16",
    metric_names="precision recall f1 accuracy_score balanced_accuracy_score".split(),
):
    hypo_files = glob.glob(dataset_folder + "/results/*")

    records = []
    for file in hypo_files:
        try:
            if os.path.isdir(file):
                with open(f"{file}/{rule_id}/metrics.json", "r") as f_:
                    model_name = file.split("/")[-1]
                    payload = json.load(f_)
                    for run_idx in range(payload["num_runs"]):
                        metrics_for_run_idx = {
                            metric: payload["all_metrics"][metric][run_idx]
                            for metric in metric_names
                        }

                        records.append(
                            {
                                **metrics_for_run_idx,
                                "run_idx": run_idx,
                                "rule_id": rule_id,
                                "model": model_name,
                            }
                        )

        except FileNotFoundError:
            logger.error(
                FileNotFoundError(
                    f"Experiment results not found: {file}/{rule_id}/metrics.json"
                )
            )
    return pd.DataFrame.from_records(records)


def violin(
    dataset_folder: str,
    rule_id: str = "r16",
    metric_name: str = "recall",
    sns_params: dict = {"inner": "point"},
    model_names: List[str] = None,
    figsize: tuple = None,
    title: str = None,
    label_rotation: float = 55,
):
    """Returns fig of a seaborn violin distribution plot for the given params.

    Parameters
    ---------
    rule_id : str
        INCOSE rule id (e.g., "r16")
    metric_name: str
        Metric name from: recall, precision, f1, accuracy_score, balanaced_accuracy_score
    sns_pararms: dict
        Pipes sns parameters to `sns.violinplot()`
    dataset_folder: str
        Name of data folder to collect metrics from. Should end with '/'.
        E.g., 'data/results/'
    model_names: List[str]
        Subset of model names to plot.  If None, plots all under dataset_folder.
    figsize: tuple
        Figsize for plotting
    title: str = None
        Plot title
    label_rotation: float = 55
        X label rotation

    """
    df_ = _get_df_for_all_runs(rule_id=rule_id, dataset_folder=dataset_folder)

    order = sorted([s_ for s_ in list(df_["model"].unique()) if s_.startswith("hypo")])

    fig, axes = plt.subplots(1, 1, figsize=figsize)

    sns.violinplot(
        data=df_,
        x="model",
        y=metric_name,
        axes=axes,
        order=order,
        **sns_params,
    ).set(ylim=(0, 1))

    axes.tick_params(axis="x", labelrotation=label_rotation)

    if title:
        axes.set_title(title)
    else:
        axes.set_title(f"{rule_id} {metric_name}")

    return fig, axes
