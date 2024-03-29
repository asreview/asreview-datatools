from pathlib import Path

import pytest

from asreviewcontrib.datatools.compose import _check_order_arg
from asreviewcontrib.datatools.compose import _check_resolve_arg
from asreviewcontrib.datatools.compose import _check_suffix
from asreviewcontrib.datatools.compose import create_composition

parent_dir = Path(__file__).parent
file_1 = Path(parent_dir, "demo_data", "dataset_1.ris")
file_2 = Path(parent_dir, "demo_data", "dataset_2.ris")

# labeling action on input paths in list = [relevant, irrelevant, labeled, unlabeled]
input_files_1 = [
    file_1,
    file_1,
    file_1,
    file_1,
]

input_files_2 = [None, None, file_1, file_2]


# test whether input and output suffixes are compatible
def test_suffixes():
    with pytest.raises(ValueError):
        _check_suffix(input_files_1, "conflicting_suffix.csv")


# test whether wrong input hierarchy/order raises error
def test_input_hierarchy():
    with pytest.raises(ValueError):
        _check_order_arg("abc")
    with pytest.raises(ValueError):
        _check_order_arg("riur")


# test whether wrong input conflict resolve raises error
def test_input_resolve():
    with pytest.raises(ValueError):
        _check_resolve_arg("fly")


def test_label_prioritization():
    # input identical datasets and overwrite everything with the relevant labels
    df_1 = create_composition(*input_files_1, order="riu")
    assert df_1["included"].value_counts()[1] == len(df_1)

    # input identical datasets and overwrite everything with the irrelevant labels
    df_2 = create_composition(*input_files_1, order="iru")
    assert df_2["included"].value_counts()[0] == len(df_2)

    # input identical datasets and overwrite everything as unlabeled
    df_3 = create_composition(*input_files_1, order="uri")
    assert df_3["included"].value_counts()[-1] == len(df_3)

    # input different datasets with some identical records, combining as labeled and
    # unlabeled data
    df_4 = create_composition(*input_files_2, order="riu")
    df_4_counts = df_4["included"].value_counts()
    assert df_4_counts[-1] == 7 and df_4_counts[0] == 3 and df_4_counts[1] == 1
