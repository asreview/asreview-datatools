from pathlib import Path

from asreviewcontrib.statistics.statistics import DataStatistics


def test_data(request):
    test_data = Path(request.fspath.dirname, "data", "embase.csv")

    stat = DataStatistics.from_file(test_data)
    assert stat.n_included() == 0
    assert stat.n_excluded() == 0
    assert stat.n_papers() == 6
    assert stat.n_missing_title() == (1, 0)
    assert stat.n_missing_abstract() == (1, 0)
    assert stat.n_unlabeled() == 6
    assert round(stat.abstract_length()) == 979
    assert round(stat.title_length()) == 93
    assert round(stat.num_keywords()) == 29


def test_labeled_data(request):
    test_data_labeled = Path(request.fspath.dirname, "data", "embase_labelled.csv")
    stat = DataStatistics.from_file(test_data_labeled)
    assert stat.n_included() == 2
    assert stat.n_excluded() == 4
    assert stat.n_papers() == 6


def test_no_kewords(request):
    test_data_nk = Path(request.fspath.dirname, "data", "embase_no_keywords.csv")
    stat = DataStatistics.from_file(test_data_nk)
    assert stat.num_keywords() is None
    assert stat.to_dict()["n_keywords"] is None
    assert stat.n_papers() == 6


def test_no_titles(request):
    test_data_nt = Path(request.fspath.dirname, "data", "embase_no_title.csv")
    stat = DataStatistics.from_file(test_data_nt)
    assert stat.title_length() is None
    assert stat.n_missing_title() == (None, None)
    assert stat.to_dict()["title_length"] is None
    assert stat.to_dict()["n_missing_title"] is None
    assert stat.n_papers() == 6


def test_no_abstracts(request):
    test_data_na = Path(request.fspath.dirname, "data", "embase_no_abstract.csv")
    stat = DataStatistics.from_file(test_data_na)
    assert stat.abstract_length() is None
    assert stat.n_missing_abstract() == (None, None)
    assert stat.to_dict()["n_missing_abstract"] is None
    assert stat.to_dict()["abstract_length"] is None
    assert stat.n_papers() == 6
