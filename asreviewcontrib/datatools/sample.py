import argparse

import pandas as pd
from asreview import ASReviewData
from asreview.data.base import load_data


def sample(input_path, output_path, nr_records, year_column="publication_year"):
    df_input = load_data(input_path).df

    # Check for presence of any variation of a year column
    if year_column not in df_input.columns:
        raise ValueError(f"• The input file should have a {year_column} column.")

    # Check if k is not too large
    if nr_records * 3 > len(df_input):
        raise ValueError(
            f"• The number of records to sample is too large."
            f"Only {len(df_input)} records are present in the input file."
            f" You are trying to sample {nr_records*3} records."
        )

    if nr_records < 1:
        raise ValueError("• The number of records to sample should be at least 1.")

    # Sort by year
    dated_records = df_input[df_input[year_column].notnull()]

    if dated_records.empty:
        raise ValueError(f"• The input file has no {year_column} values.")

    if len(dated_records) < nr_records * 2:
        raise ValueError("• Not enough dated records to sample from.")

    sorted_records = dated_records.sort_values(year_column, ascending=True)

    # Take k old and k new records
    old_records = sorted_records.head(nr_records)
    new_records = sorted_records.tail(nr_records)

    # Sample k records without overlap with old/new records
    records_to_exclude = pd.concat([old_records, new_records]).index
    remaining_records = df_input[~df_input.index.isin(records_to_exclude)]

    sampled_records = remaining_records.sample(nr_records)

    # Combine old, new, and sampled records
    df_out = pd.concat([old_records, sampled_records, new_records])

    asdata = ASReviewData(df=df_out)
    asdata.to_file(output_path)


def _parse_arguments_sample():
    parser = argparse.ArgumentParser(prog="asreview data sample")
    parser.add_argument("input_path", type=str, help="The input file path.")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument(
        "nr_records",
        type=int,
        help="The amount of records for old, random, and new records each.",
    )
    parser.add_argument(
        "--year_column",
        default="publication_year",
        type=str,
        help="The name of the column containing the publication year.",
    )

    return parser
