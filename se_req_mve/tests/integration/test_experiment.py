"""Tests experimentation framework"""
import os
import shutil

import pytest

from se_req_mve.features.experiment import run_experiment
from se_req_mve.services.aoai_client import get_credentials_aoai


@pytest.fixture
def dataset_path():
    return "src/tests/data/sample_reqs.json"


@pytest.fixture
def model_path():
    return "src/models/experiment_flow"


@pytest.fixture
def eval_path():
    return "src/models/evaluation"


@pytest.fixture
def rules_path():
    return "../../../src/tests/data/sample_rules.json"


@pytest.fixture
def creds():
    return get_credentials_aoai()


def test_run_experiment(dataset_path, model_path, rules_path, creds):
    output_dir = "tmp_dir"

    exper_out = run_experiment(
        dataset_path=dataset_path,
        pf_model_path=model_path,
        input_data_path=rules_path,
        aoai_creds=creds,
        rule_id="r16",
        output_dir=output_dir,
        variant="hypothesis001",
    )

    # assert experiment concluded without errors
    assert exper_out

    # verify that outputs file were written
    assert os.path.isfile(exper_out.metrics_file)

    # clean up files
    shutil.rmtree(output_dir)
    return
