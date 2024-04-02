import argparse
import warnings
from pathlib import Path

import pandas as pd
from asreview import ASReviewData
from asreview.data.base import load_data


def _check_suffix(input_file, output_file):
    # Also raises ValueError on URLs that do not end with a file extension
    suffixes = [Path(input_file).suffix, Path(output_file).suffix]

    set_ris = {".txt", ".ris"}
    set_tabular = {".csv", ".tab", ".tsv", ".xlsx"}
    set_suffixes = set(suffixes)

    if len(set(suffixes)) > 1:
        if not (set_suffixes.issubset(set_ris) or set_suffixes.issubset(set_tabular)):
            raise ValueError(
                "• Several file types were given; The input file and the output file should be of the same "
                "type. "
            )


def sample(output_path, input_path, nr_records):
    _check_suffix(input_path, output_path)

    df_input = load_data(input_path).df

    # Check for presence of any variation of a year column
    if "publication_year" not in df_input.columns:
        raise ValueError("• The input file should have a 'publication_year' column.")

    # Check if x is not too large
    if nr_records*3 > len(df_input):
        warnings.warn(
            f"• The number of records to sample is larger than the number of records in the input file. "
            f"Only {len(df_input)} records are present in the input file."
            f" You are trying to sample {nr_records*3} records."
        )

    # Sort by year
    dated_records = df_input[df_input["publication_year"].notnull()]

    if dated_records.empty:
        raise ValueError("• The input file should have at least one record with a 'publication_year'.")
    
    if len(dated_records) < nr_records*2:
        raise ValueError(f"• The input file contains only {len(dated_records)} dated records.")

    sorted_records = dated_records.sort_values("publication_year", ascending=True)

    # Take x old and x new records
    old_records = sorted_records.head(nr_records)
    new_records = sorted_records.tail(nr_records)

    # Sample x records without overlap with old/new records
    records_to_exclude = pd.concat([old_records, new_records]).index
    remaining_records = df_input[~df_input.index.isin(records_to_exclude)]

    sampled_records = remaining_records.sample(nr_records)

    # Combine old, new, and sampled records
    df_out = pd.concat([old_records, sampled_records, new_records])
    
    asdata = ASReviewData(df=df_out)
    asdata.to_file(output_path)


def _parse_arguments_sample():
    parser = argparse.ArgumentParser(prog="asreview data sample")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument("input_path", type=str, help="The input file path.")
    parser.add_argument("nr_records", type=int, help="The amount of records for old, random, and new records each.")

    return parser