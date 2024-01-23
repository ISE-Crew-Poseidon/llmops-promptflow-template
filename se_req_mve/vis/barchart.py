"""Utils for producing grouped bar charts. Useful for comparing metrics across several modeling approaches"""
import matplotlib.pyplot as plt
import pandas as pd
from numpy import arange


def prepare_mean_metrics_for_plot(
    metrics_df: pd.DataFrame = None, rule_id: str = None
) -> None:
    # create a slice of the dataframe for the given rule
    metrics_df_slice = (
        metrics_df[metrics_df["rule"] == rule_id].set_index("model").copy()
    )

    # set the model order to go hypothesis001, hypothesis002 etc.
    model_names = metrics_df_slice.index.unique().tolist()
    model_name_order = [x for x in model_names]
    metrics_df_slice = metrics_df_slice.loc[model_name_order]

    return metrics_df_slice


def plot_mean_metrics(
    metrics_df_one_rule: pd.DataFrame = None,
    hypotheses: list = [],
    metrics_names: list = ["precision", "recall", "f1"],
    title: str = "Mean metrics",
    figsize: tuple = None,
) -> None:
    """
    Plot precision, recall, and f1 in metrics_df with error bars for the respective 2std values for one rule.
    """

    # filter out for hypotheses of interest
    metrics_df_one_rule = metrics_df_one_rule.copy()
    metrics_df_one_rule = metrics_df_one_rule[
        metrics_df_one_rule.index.isin(hypotheses)
    ]

    # plot precision, recall, f1 with their respective 2std on the same graph
    fig, axes = plt.subplots(1, 1, figsize=figsize)
    axes.set_ylim(0, 1)
    X_axis = arange(len(metrics_df_one_rule.index.tolist()))
    interval = (1 / len(metrics_names)) - 0.1
    ticks = [-interval * 1.5 + interval * num for num in range(len(metrics_names))]
    colors = ["b", "orange", "g", "c", "purple"]
    for i, metric in enumerate(metrics_names):
        axes.bar(
            X_axis + ticks[i],
            metrics_df_one_rule[metric],
            interval,
            label=metric.replace("_", " "),
            color=colors[i],
        )
        if i == 0:
            axes.errorbar(
                X_axis + ticks[i],
                metrics_df_one_rule[metric],
                yerr=metrics_df_one_rule[metric + "_2std"],
                fmt="o",
                color="r",
                label="95% C.I.",
            )
        else:
            axes.errorbar(
                X_axis + ticks[i],
                metrics_df_one_rule[metric],
                yerr=metrics_df_one_rule[metric + "_2std"],
                fmt="o",
                color="r",
            )
    axes.set_xticks(X_axis, metrics_df_one_rule.index.tolist(), rotation="vertical")
    axes.set_title(title)
    handles, labels = axes.get_legend_handles_labels()
    order = [x for x in range(len(metrics_names) + 1) if x != 1] + [1]
    axes.legend(
        [handles[idx] for idx in order],
        [labels[idx] for idx in order],
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    axes.grid(color="grey", linestyle="--", linewidth=0.5, axis="y")

    return fig, axes
