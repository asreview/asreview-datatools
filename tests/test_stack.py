from pathlib import Path

from asreview.data import ASReviewData

from asreviewcontrib.datatools.stack import vstack

test_dir = Path(__file__).parent
file_1 = Path(test_dir, "demo_data", "dataset_1.ris")
file_2 = Path(test_dir, "demo_data", "dataset_2.ris")


def test_stack(tmpdir):
    output_path = Path(tmpdir, "test_output.ris")
    vstack(output_path, [file_1, file_2])
    as_test = ASReviewData.from_file(output_path)

    assert len(as_test.df) == 14
    assert as_test.df["included"].value_counts()[-1] == 9
    assert as_test.df["included"].value_counts()[0] == 3
    assert as_test.df["included"].value_counts()[1] == 2
