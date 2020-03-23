import os
from pathlib import Path

from asreview.settings import ASReviewSettings
from asreview import review_simulate

from asreviewcontrib.statistics.statistics import StateStatistics


def test_state():
    os.makedirs(Path("tests", "output"), exist_ok=True)
    state_fp = Path("tests", "output", "test.h5")
    state_fp_2 = Path("tests", "output", "test2.h5")
    data_fp = Path("tests", "data", "embase_labelled.csv")
    for fp in [state_fp, state_fp_2]:
        try:
            os.remove(fp)
        except FileNotFoundError:
            pass
        review_simulate(data_fp, state_file=fp, n_prior_included=1,
                        n_prior_excluded=1, model="nb",
                        feature_extraction="tfidf")

    with StateStatistics.from_path(state_fp) as stat:
        check_stat(stat)

    with StateStatistics.from_path(Path("tests", "output")) as stat:
        check_stat(stat, 2)

    os.remove(state_fp)
    os.remove(state_fp_2)


def check_stat(stat, n_state_fp=1):
    stat_dict = stat.to_dict()
    assert stat_dict is not None
    assert stat.wss(100) is not None
    assert stat.rrf(10) is not None
    assert isinstance(stat.settings, ASReviewSettings)
    assert stat_dict["general"]["n_queries"][0] == 5
    assert stat_dict["general"]["n_states"] == n_state_fp
    assert stat_dict["general"]["n_papers"] == 6
    assert stat_dict["general"]["n_included"] == 2
    assert stat_dict["general"]["n_excluded"] == 4
