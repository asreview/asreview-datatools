import unittest
from pathlib import Path

from asreviewcontrib.datatools.compose import compose


class TestCompose(unittest.TestCase):
    # paths for demo data for testing
    path_dataset_1_csv = Path("test", "demo_data", "dataset_1.ris")
    path_dataset_2_csv = Path("test", "demo_data", "dataset_2.ris")

    # labeling action on input paths in list = [relevant, irrelevant, labeled, unlabeled]
    input_files_1 = [
        path_dataset_1_csv,
        path_dataset_1_csv,
        path_dataset_1_csv,
        path_dataset_1_csv,
    ]
    input_files_2 = [None, None, path_dataset_1_csv, path_dataset_2_csv]

    # test whether using different input and output file types raises a ValueError
    def test_suffixes(self):
        self.assertRaises(
            ValueError,
            compose,
            "some_file.csv",
            self.input_files_1,
            pid="doi",
            order="riu",
            resolve="continue",
        )

    # some test cases to assert prioritization of labels
    def test_label_prioritization(self):
        # input identical datasets and overwrite everything with the relevant labels
        df_1 = compose("just_a_test.ris", self.input_files_1, order="riu")
        assert df_1["included"].value_counts()[1] == len(df_1)

        # input identical datasets and overwrite everything with the irrelevant labels
        df_2 = compose("just_a_test.ris", self.input_files_1, order="iru")
        assert df_2["included"].value_counts()[0] == len(df_2)

        # input identical datasets and overwrite everything as unlabeled
        df_3 = compose("just_a_test.ris", self.input_files_1, order="uri")
        assert df_3["included"].value_counts()[-1] == len(df_3)

        # input different datasets with some identical records, combining as labeled and unlabeled data
        df_4 = compose("just_a_test.ris", self.input_files_2, order="riu")
        df_4_counts = df_4["included"].value_counts()
        assert df_4_counts[-1] == 7 and df_4_counts[0] == 3 and df_4_counts[1] == 1


if __name__ == "__main__":
    unittest.main(buffer=True)
