from pathlib import Path

import pytest

from asreview.data import ASReviewData
from asreviewcontrib.datatools.stack import stack


parent_dir = Path(__file__).parent
file_1 = Path(parent_dir, "demo_data", "dataset_1.ris")
file_2 = Path(parent_dir, "demo_data", "dataset_2.ris")


def test_stack(tmpdir):
    output_path = Path(tmpdir, "test_output.ris")
    stack(output_path, [file_1, file_2])
    as_test = ASReviewData.from_file(output_path)
    print(as_test.df)
    print("yay?")
    assert 1 == 1
