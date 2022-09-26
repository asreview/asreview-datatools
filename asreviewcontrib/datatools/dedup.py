import argparse

import pandas as pd
from pandas.api.types import is_string_dtype


def dedup(asdata, pid='doi'):
    if pid in asdata.df.columns:
        # in case of strings, strip whitespaces and replace empty strings with None
        if is_string_dtype(asdata.df[pid]):
            s_pid = asdata.df[pid].str.strip().replace("", None)

        # remove records based on duplicate PIDs
        asdata.df = asdata.df[(~s_pid.duplicated()) | (s_pid.isnull())].reset_index(drop=True)

    # get the texts and clean them
    s = pd.Series(asdata.texts) \
        .str.replace("[^A-Za-z0-9]", "", regex=True) \
        .str.lower()

    # remove records based on duplicate texts
    asdata.df = asdata.df[~s.duplicated()].reset_index(drop=True)

    return asdata


def _parse_arguments_dedup():
    parser = argparse.ArgumentParser(prog="asreview data dedup")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("--output_path", "-o", default=None, type=str, help="The file path of the dataset.")
    parser.add_argument("--pid", default='doi', type=str,
                        help="Persistent identifier used for deduplication. Default: doi.")

    return parser
