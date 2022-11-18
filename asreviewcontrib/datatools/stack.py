import argparse
import warnings
from pathlib import Path

import pandas as pd
from asreview import ASReviewData
from asreview.data.base import load_data


def _check_suffix(input_files, output_file):
    # Also raises ValueError on URLs that do not end with a file extension
    suffixes = [Path(item).suffix for item in input_files if item is not None]
    suffixes.append(Path(output_file).suffix)

    set_ris = {".txt", ".ris"}
    set_tabular = {".csv", ".tab", ".tsv", ".xlsx"}
    set_suffixes = set(suffixes)

    if len(set(suffixes)) > 1:
        if not (set_suffixes.issubset(set_ris) or set_suffixes.issubset(set_tabular)):
            raise ValueError(
                "• Several file types were given; All input files, as well as the output file should be of the same "
                "type. "
            )


def vstack(output_file, input_files):
    _check_suffix(input_files, output_file)

    list_dfs = [load_data(item).df for item in input_files]
    df_vstacked = pd.concat(list_dfs).reset_index(drop=True)
    as_vstacked = ASReviewData(df=df_vstacked)

    # supress warning about certain columns not exported to .ris output
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        as_vstacked.to_file(output_file)


def _parse_arguments_vstack():
    parser = argparse.ArgumentParser(prog="asreview data vstack")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument(
        "datasets", type=str, nargs="+", help="Any number of datasets to stack vertically."
    )

    return parser
