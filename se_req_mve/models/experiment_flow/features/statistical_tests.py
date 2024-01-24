"""Statistical testing: student's t-test, welchs t-test, fischer exact test"""
import itertools
import json
from typing import List

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp


def student_t_test(
    hypo_id: str = "hypothesis001",
    rule_id: str = "r16",
    metric_name: str = "recall",
    baseline_metrics_df: pd.DataFrame = None,
):
    """Runs a one-sample Student's t-test

    Baseline metrics dataframe expects 'rule_id' as index and
    'metric_name' as a column
    """
    null_metric = baseline_metrics_df.loc[rule_id, metric_name]
    if null_metric == np.nan:
        return [np.nan, np.nan]

    sample_metric_file = f"../data/results/{hypo_id}/{rule_id}/metrics.json"
    with open(sample_metric_file, "r") as f_:
        data = json.load(f_)
        data = data["all_metrics"][metric_name]

    t_stat, p_value = ttest_1samp(data, popmean=null_metric)
    return t_stat, p_value, null_metric, np.mean(data)


def loop_hypo_test(
    hypotheses: List[str] = [f"hypothesis00{idx}" for idx in [1, 2, 3, 6]],
    metrics: List[
        str
    ] = "recall precision f1 accuracy_score balanced_accuracy_score".split(),
    rules: List[str] = [f"r{idx}" for idx in [3, 7, 8, 9, 16, 18, 30, 31]],
    baseline_metrics_filepath: str = None,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Loops over a product of the input parameters (hypotheses, metrics, rules)
    and applies `hypo_test()`.  Results are returned in a dataframe.
    """

    baseline_df = pd.read_csv(baseline_metrics_filepath, index_col=0)

    records = []
    for hypothesis, metric_name, rule_id in itertools.product(
        hypotheses, metrics, rules
    ):
        t_student, pval_student, null_metric, sample_metric = student_t_test(
            hypo_id=hypothesis,
            rule_id=rule_id,
            metric_name=metric_name,
            baseline_metrics_df=baseline_df,
        )

        records.append(
            {
                "hypothesis": hypothesis,
                "metric_name": metric_name,
                "rule_id": rule_id,
                "null_metric": null_metric,
                "sample_metric": sample_metric,
                "t_student": t_student,
                "pval_student": pval_student,
                "reject_h0_twotail": (pval_student < alpha),
                "reject_h0_onetail": ((pval_student / 2) < alpha) and (t_student > 0),
            }
        )

    return pd.DataFrame.from_records(records)
