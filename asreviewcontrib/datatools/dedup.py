import argparse

import pandas as pd

from asreview.data import load_data


def dedup(input_path, output_path=None):
    # read data in ASReview data object
    asdata = load_data(input_path)

    # get the texts and clean them
    s = pd.Series(asdata.texts) \
        .str.replace("[^A-Za-z0-9]", "", regex=True) \
        .str.lower()

    # remove the records
    asdata.df = asdata.df[~s.duplicated()]

    # count duplicates
    n_dup = len(s) - len(asdata.df)

    # export the file
    if output_path:
        asdata.to_file(output_path)
        print(f"Removed {n_dup} records from dataset with {len(s)} records.")
    else:
        print(f"Found {n_dup} records in dataset with {len(s)} records.")




def _parse_arguments_dedup():
    parser = argparse.ArgumentParser(prog="asreview data dedup")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("--output_path", "-o", default=None, type=str, help="The file path of the dataset.")

    return parser
