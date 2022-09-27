import argparse

import pandas as pd
from pandas.api.types import is_string_dtype


def dedup(asdata, pid='doi'):
    if pid in asdata.df.columns:
        # in case of strings, strip whitespaces and replace empty strings with None
        if is_string_dtype(asdata.df[pid]):
            s_pid = asdata.df[pid].str.strip().replace("", None)
        else:
            s_pid = asdata.df[pid]

        # save boolean series for duplicates based on persistent identifiers
        s_dups_pid = ((s_pid.duplicated()) & (s_pid.notnull()))
    else:
        s_dups_pid = None

    # get the texts and clean them
    s = pd.Series(asdata.texts) \
        .str.replace("[^A-Za-z0-9]", "", regex=True) \
        .str.lower()

    # save boolean series for duplicates based on titles/abstracts
    s_dups_text = s.duplicated()

    # final boolean series for all duplicates
    if s_dups_pid is not None:
        s_dups = s_dups_pid | s_dups_text
    else:
        s_dups = s_dups_text

    asdata.df = asdata.df[~s_dups].reset_index(drop=True)

    return asdata


def _parse_arguments_dedup():
    parser = argparse.ArgumentParser(prog="asreview data dedup")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("--output_path", "-o", default=None, type=str, help="The file path of the dataset.")
    parser.add_argument("--pid", default='doi', type=str,
                        help="Persistent identifier used for deduplication. Default: doi.")

    return parser
