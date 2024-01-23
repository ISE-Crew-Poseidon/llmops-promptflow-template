"""Misc utility functions"""
import glob
import json
import os
from typing import List

import pandas as pd
from numpy import mean, random, std

from src.utils.logger import llmops_logger

logger = llmops_logger()


def average_metrics(all_metrics_list: List):
    """Reformats metrics collected from src.features.Replicate objects
    into Dict[str, List] from List[Dict].  Also produces mean_metrics.
    """
    all_metrics = {k: [d[k] for d in all_metrics_list] for k in all_metrics_list[0]}
    mean_metrics = {
        k: mean(vals)
        for k, vals in all_metrics.items()
        if k in "recall precision f1 accuracy_score balanced_accuracy_score".split()
    }
    return all_metrics, mean_metrics


def collect_mean_metrics_for_all_rules(
    experiment_results_folder: str,
    serialize_to_file: bool = True,
) -> pd.DataFrame:
    """Collect mean metrics from input experiment_output folder into a single dataframe
    indexed by rule (given by `display_name`). Also, calculates standard deviation for each
    metric across all runs and adds the standard deviation values to the dataframe.
    """
    if not experiment_results_folder:
        logger.error("Missing required input: experiment_results_folder")
        raise ValueError("Required input: experiment_results_folder")
    experiment_results = {}
    for f_ in glob.glob(experiment_results_folder + "*/metrics.json"):
        with open(f_, "r") as metrics_file:
            metrics_for_rule = json.load(metrics_file)
            mean_dict = metrics_for_rule["mean_metrics"]
            std_dict = {}
            for x in metrics_for_rule["all_metrics"]:
                if x != "confusion_matrix":
                    std_dict[x + "_2std"] = 2 * std(metrics_for_rule["all_metrics"][x])

            mean_dict.update(std_dict)
            experiment_results[metrics_for_rule["rule_name"]] = mean_dict

    df_ = pd.DataFrame.from_records(experiment_results).T
    col_order = [
        "recall",
        "recall_2std",
        "precision",
        "precision_2std",
        "f1",
        "f1_2std",
        "accuracy_score",
        "accuracy_score_2std",
        "balanced_accuracy_score",
        "balanced_accuracy_score_2std",
    ]
    df_ = df_[col_order].round(3)
    if serialize_to_file:
        df_.to_csv(experiment_results_folder + "mean_metrics.csv")

    return df_


def collect_mean_metrics_for_all_models(
    experiment_results_folder: str,
    serialize_to_file: bool = False,
) -> dict:
    """Aggregate all mean_metrics.csv files from experiment_results_folder into 5 separate dataframes
    (accuracy, balanced accuracy, f1, recall, precision) indexed by model name with the rules as column values.
    Return as a dictionary of dataframes.
    If serialize_to_file is true then output the 5 dataframes to a new folder: <experiment_results_folder>/all.
    """

    # collect all model results
    experiment_results_folder += "/results"
    model_folders = [
        os.path.join(experiment_results_folder, x)
        for x in os.listdir(experiment_results_folder)
        if os.path.isdir(os.path.join(experiment_results_folder, x))
        and x not in ["all", "statistical_tests"]
    ]
    results_paths = [os.path.join(x, "mean_metrics.csv") for x in model_folders]

    # append all model results together
    full_df = pd.DataFrame()
    for r in results_paths:
        df = pd.read_csv(r).rename(columns={"Unnamed: 0": "rule"})
        df["model"] = r.split("/")[-2]
        full_df = pd.concat([full_df, df])

    # write out to file for later reference
    if serialize_to_file:
        output_dir = os.path.join(experiment_results_folder, "all")
        os.makedirs(output_dir, exist_ok=True)
        full_df.to_csv(
            os.path.join(output_dir, "results/mean_metrics.csv"), index=False
        )

    return full_df


def simulate_baseline(
    baseline_metrics_file: str,
    output_dir: str = None,
    num_runs: int = 7,
):
    """Samples from normal distribution to generate sample points for metrics.
    Saves to a metrics.json file in ExperimentOutput schema.
    """
    df_ = pd.read_csv(baseline_metrics_file)

    for _, row_ in df_.iterrows():
        rule_id = row_["rule"]
        output_dir_for_rule = f"{output_dir}/{rule_id}/"
        os.makedirs(output_dir_for_rule, exist_ok=True)

        sampled_metrics_dict = {}
        for (
            metric_name
        ) in "precision recall f1 accuracy_score balanced_accuracy_score".split():
            m_ = float(row_[metric_name])
            m_std = float(row_[metric_name + "_2std"]) / 2

            sampled_metrics_dict[metric_name] = list(random.normal(m_, m_std, num_runs))

        payload = {
            "display_name": rule_id,
            "all_metrics": sampled_metrics_dict,
            "mean_metrics": None,
            "dataset_ver": "requirements_v1.json",
            "num_runs": num_runs,
        }

        with open(output_dir_for_rule + "results/metrics.json", "w") as f_:
            json.dump(payload, f_)

        return payload
