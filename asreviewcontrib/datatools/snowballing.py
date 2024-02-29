import argparse
from pathlib import Path

import pandas as pd
import pyalex
from asreview import ASReviewData, load_data
from pyalex import Works

# Maximum number of statements joined by a logical OR in a call to OpenAlex.
OPENALEX_MAX_OR_LENGTH = 100
OPENALEX_MAX_PAGE_LENGTH = 200
# OpenAlex data fields to retrieve.
USED_FIELDS = [
    "id",
    "doi",
    "title",
    "abstract_inverted_index",
    "referenced_works",
    "publication_date",
]


def forward_snowballing(identifiers: list[str]) -> dict[str, list[dict]]:
    """Get all works citing a work with the OpenAlex identifier from the list.

    Parameters
    ----------
    identifiers : list[str]
        List of OpenAlex identifiers.

    Returns
    -------
    dict[str, list[dict]]
        Dictionary of the form
            `{input OpenAlex identifier : list of OpenAlex works}`
        where each work in the list references the work with the input identifier and
        it is a dictionary of the form `{field_name : field_value}`.
    """
    citing_works = {}
    for idx, openalex_id in enumerate(identifiers):
        print(f"{idx}. Getting cited works for {openalex_id}")
        works_citing_id = Works().filter(cites=openalex_id).select(USED_FIELDS).get()
        citing_works[openalex_id] = [
            {
                key: work[key]
                for key in [
                    col if col != "abstract_inverted_index" else "abstract"
                    for col in USED_FIELDS
                ]
            }
            for work in works_citing_id
        ]
    return citing_works


def backward_snowballing(identifiers: list[str]) -> dict[str, list[dict]]:
    """Get all works cited by a work with the OpenAlex identifier from the list.

    Parameters
    ----------
    identifiers : list[str]
        List of OpenAlex identifiers.

    Returns
    -------
    dict[str, list[dict]]
        Dictionary of the form
            `{input OpenAlex identifier : list of OpenAlex works}`
        where each work in the list is referenced by the work with the input identifier
        and it is a dictionary of the form `{field_name : field_value}`.
    """
    # Get the referenced works.
    referenced_works = {}
    page_length = min(OPENALEX_MAX_OR_LENGTH, OPENALEX_MAX_PAGE_LENGTH)
    for i in range(0, len(identifiers), page_length):
        fltr = "|".join(identifiers[i : i + page_length])
        pager = (
            Works()
            .filter(openalex=fltr)
            .select("id,referenced_works")
            .paginate(per_page=page_length)
        )
        for page in pager:
            for work in page:
                referenced_works[work["id"]] = work["referenced_works"]

    # Get the fields for the referenced works.
    all_identifiers = []
    for reference_list in referenced_works.values():
        all_identifiers += reference_list

    all_referenced_works = {}
    for i in range(0, len(all_identifiers), page_length):
        fltr = "|".join(all_identifiers[i : i + page_length])
        pager = (
            Works()
            .filter(openalex=fltr)
            .select(USED_FIELDS)
            .paginate(per_page=page_length)
        )
        for page in pager:
            for work in page:
                all_referenced_works[work["id"]] = {
                    key: work[key]
                    for key in [
                        col if col != "abstract_inverted_index" else "abstract"
                        for col in USED_FIELDS
                    ]
                }

    # Connect the referenced works back to the input works.
    for identifier, ref_id_list in referenced_works.items():
        referenced_works[identifier] = [
            all_referenced_works[ref_id] for ref_id in ref_id_list
        ]
    return referenced_works


def snowballing(
    input_path: Path,
    output_path: Path,
    forward: bool,
    backward: bool,
    use_all: bool = False,
    email: str = None,
) -> None:
    data = load_data(input_path)

    if not (forward or backward):
        raise ValueError("At least one of 'forward' or 'backward' should be True.")

    if "openalex_id" not in data.df.columns:
        raise ValueError(
            "Dataset should contain a column 'openalex_id' containing OpenAlex"
            " identifiers."
        )

    if not use_all:
        identifiers = data.df.loc[
            data.included & data.df.openalex_id.notna(), "openalex_id"
        ].to_list()
    else:
        identifiers = data.df["openalex_id"].dropna().to_list()

    if email is not None:
        pyalex.config.email = email

    if forward:
        forward_data = forward_snowballing(identifiers)
    else:
        forward_data = {}
    if backward:
        backward_data = backward_snowballing(identifiers)
    else:
        backward_data = {}

    all_works = []
    for works_list in forward_data.values():
        all_works += works_list
    for works_list in backward_data.values():
        all_works += works_list
    output_data = pd.DataFrame(all_works)
    output_data.drop_duplicates(subset=["id"], inplace=True)
    output_data.rename({"id": "openalex_id"}, axis=1, inplace=True)
    output_data = ASReviewData(output_data)
    output_data.to_file(output_path)


def _parse_arguments_snowballing():
    parser = argparse.ArgumentParser(prog="asreview data snowballing")
    parser.add_argument(
        "input_path", type=str, help="The file path of the input dataset."
    )
    parser.add_argument(
        "output_path", type=str, help="The file path of the output dataset."
    )
    parser.add_argument("--forward", type=bool, help="Do forward snowballing.")
    parser.add_argument("--backward", type=bool, help="Do backward snowballing.")
    parser.add_argument(
        "--use_all",
        type=bool,
        default=False,
        required=False,
        help=(
            "Do snowballing on all records in the dataset, not just the included ones."
        ),
    )
    parser.add_argument(
        "--email",
        type=str,
        required=False,
        help=(
            "Email address to send along with requests to OpenAlex. This will make"
            " requests faster. See also "
            "https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool"
        ),
    )
    return parser
