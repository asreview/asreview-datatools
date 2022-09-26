import argparse

import pandas as pd


def dedup(asdata, pid='doi'):
    if pid in asdata.df.columns:
        # replace NaN values with empty string to prevent astype(str) from creating literal 'NaN' string
        asdata.df[pid] = asdata.df[pid].fillna('')

        # convert to string to support non-string types, strip whitespaces and replace empty strings with NaN values
        s_pid = asdata.df[pid].astype(str).str.strip().replace("", None)

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
    parser.add_argument("--pid", default='doi', type=str, help="Persistent identifier used for deduplication. Default: doi.")

    return parser
