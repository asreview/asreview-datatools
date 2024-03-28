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


def sample(output_file, input_file, x):
    _check_suffix(input_file, output_file)

    df_input = load_data(input_file).df

    # Check for presence of any variation of a year column
    if "year" not in df_input.columns:
        raise ValueError("• The input file should have a 'year' column.")

    # Check if x is not too large
    if x*3 > len(df_input):
        warnings.warn(
            f"• The number of records to sample is larger than the number of records in the input file. "
            f"Only {len(df_input)} records are present in the input file."
            f" You are trying to sample {x*3} records."
        )

    # Sort by year
    dated_records = df_input[df_input["year"].notnull()]
    sorted_records = dated_records.sort_values("year", ascending=True)

    # Take x old and x new records
    old_records = sorted_records.head(x)
    new_records = sorted_records.tail(x)

    # Sample x records without overlap with old/new records
    sampled_records = sorted_records[~(old_records | new_records)].sample(x)

    # Combine old, new, and sampled records
    df_out = pd.concat([old_records, sampled_records, new_records])
    
    asdata = ASReviewData(df=df_out)
    asdata.to_file(output_file)


def _parse_arguments_sample():
    parser = argparse.ArgumentParser(prog="asreview data sample")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument(
        "datasets", type=str, nargs="+", help="Any datasets to sample a calibration set for."
    )

    return parser