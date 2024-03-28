from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pyalex
from asreview import ASReviewData
from asreview import load_data

# Maximum number of statements joined by a logical OR in a call to OpenAlex.
OPENALEX_MAX_OR_LENGTH = 100
OPENALEX_MAX_PAGE_LENGTH = 200
OPENALEX_PREFIX = "https://openalex.org/"
DOI_PREFIX = "https://doi.org/"

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
        print(f"{idx}. Getting works citing {openalex_id}")
        pager = (
            pyalex.Works()
            .filter(cites=openalex_id)
            .select(USED_FIELDS)
            .paginate(per_page=OPENALEX_MAX_PAGE_LENGTH, n_max=None)
        )
        citing_works[openalex_id] = []
        for page in pager:
            citing_works[openalex_id] += [
                {
                    key: work[key]
                    for key in [
                        col if col != "abstract_inverted_index" else "abstract"
                        for col in USED_FIELDS
                    ]
                }
                for work in page
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
        print(f"Getting works citing records {i}-{i+page_length}")
        # We need to remove the prefix here because otherwise the URL is too long.
        fltr = "|".join(
            identifier.removeprefix(OPENALEX_PREFIX)
            for identifier in identifiers[i : i + page_length]
        )
        for work in (
            pyalex.Works()
            .filter(openalex=fltr)
            .select("id,referenced_works")
            .get(per_page=page_length)
        ):
            referenced_works[work["id"]] = work["referenced_works"]

    # Get the fields for the referenced works.
    all_identifiers = []
    for reference_list in referenced_works.values():
        all_identifiers += reference_list
    all_identifiers = list(set(all_identifiers))
    print(f"Found {len(all_identifiers)} records")

    all_referenced_works = {}
    for i in range(0, len(all_identifiers), page_length):
        # We need to remove the prefix here because otherwise the URL is too long.
        fltr = "|".join(
            identifier.removeprefix(OPENALEX_PREFIX)
            for identifier in all_identifiers[i : i + page_length]
        )
        for work in (
            pyalex.Works()
            .filter(openalex=fltr)
            .select(USED_FIELDS)
            .get(per_page=page_length)
        ):
            all_referenced_works[work["id"]] = {
                key: work[key]
                for key in [
                    col if col != "abstract_inverted_index" else "abstract"
                    for col in USED_FIELDS
                ]
            }

    # Connect the referenced works back to the input works.
    output = {}
    for identifier, ref_id_list in referenced_works.items():
        # We need the last check if 'ref_id' is in 'all_referenced_works': If a work
        # references an ID that redirects to another ID, it won't be present here.
        # Example: https://openalex.org/W2015370450 has in the references the identifier
        # https://openalex.org/W2008744335, but this redirects to
        # https://openalex.org/W4233569835
        output[identifier] = [
            all_referenced_works[ref_id]
            for ref_id in ref_id_list
            if ref_id in all_referenced_works
        ]
    return output


def openalex_from_doi(dois: list[str]) -> dict[str, str]:
    """Get the OpenAlex identifiers corresponding to a list of DOIs.

    Parameters
    ----------
    dois : list[str]
        List of DOIs.

    Returns
    -------
    dict[str, str]
        Dictionary {doi: openalex_id}. If there was no OpenAlex identifier found for a
        DOI, the corresponding value will be None.
    """
    page_length = min(OPENALEX_MAX_OR_LENGTH, OPENALEX_MAX_PAGE_LENGTH)
    id_mapping = {doi.removeprefix(DOI_PREFIX): None for doi in dois}
    for i in range(0, len(dois), page_length):
        fltr = "|".join(dois[i : i + page_length])
        for work in (
            pyalex.Works()
            .filter(doi=fltr)
            .select(["id", "doi"])
            .get(per_page=page_length)
        ):
            id_mapping[work["doi"].removeprefix(DOI_PREFIX)] = work["id"]
    return id_mapping


def snowball(
    input_path: Path,
    output_path: Path,
    forward: bool,
    backward: bool,
    use_all: bool = False,
    email: str = None,
) -> None:
    """Perform snowballing on an ASReview dataset.

    Parameters
    ----------
    input_path : Path
        Location of the input ASReview dataset.
    output_path : Path
        Location where to save the output dataset.
    forward : bool
        Perform forward snowballing. At least one of `forward` or `backward` should be
        True.
    backward : bool
        Perform backward snowballing. At least one of `forward` or `backward` should be
        True.
    use_all : bool, optional
        Perform snowballing on all records in the dataset or only the included
        records, by default False
    email : str, optional
        Email address to send along with request to OpenAlex, by default None

    Raises
    ------
    ValueError
        If `forward` and `backward` are both False.
    ValueError
        If the dataset contains no column name `openalex_id` and no column names `doi`.
    """
    if not (forward or backward):
        raise ValueError("At least one of 'forward' or 'backward' should be True.")

    data = load_data(input_path)
    if use_all or (data.included is None):
        data = data.df
    else:
        data = data.df.loc[data.included.astype(bool)]

    # Add OpenAlex identifiers if not available.
    if "openalex_id" not in data.columns:
        if "doi" not in data.columns:
            raise ValueError(
                "Dataset should contain a column 'openalex_id' containing OpenAlex"
                " identifiers or a column 'doi' containing DOIs."
            )
        id_mapping = openalex_from_doi(data.doi.dropna().to_list())
        n_openalex_ids = len(
            [
                openalex_id
                for openalex_id in id_mapping.values()
                if openalex_id is not None
            ]
        )
        print(
            f"Found OpenAlex identifiers for {n_openalex_ids} out of {len(data)}"
            " records. Performing snowballing for those records."
        )
        data["openalex_id"] = None
        data.loc[data.doi.notna(), "openalex_id"] = (
            data.loc[data.doi.notna(), "doi"]
            .str.removeprefix(DOI_PREFIX)
            .apply(lambda doi: id_mapping[doi])
        )

    identifiers = data["openalex_id"].dropna().to_list()

    if email is not None:
        pyalex.config.email = email

    if forward:
        print("Starting forward snowballing")
        forward_data = forward_snowballing(identifiers)
    else:
        forward_data = {}
    if backward:
        print("Starting backward snowballing")
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
    print("Saved dataset")


def _parse_arguments_snowball():
    parser = argparse.ArgumentParser(prog="asreview data snowballing")
    parser.add_argument(
        "input_path", type=str, help="The file path of the input dataset."
    )
    parser.add_argument(
        "output_path", type=str, help="The file path of the output dataset."
    )
    parser.add_argument(
        "--forward", "-f", action="store_true", help="Do forward snowballing."
    )
    parser.add_argument(
        "--backward", "-b", action="store_true", help="Do backward snowballing."
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        dest="use_all",
        help=(
            "Do snowballing on all records in the dataset, not just the included ones."
        ),
    )
    parser.add_argument(
        "--email",
        "-e",
        type=str,
        required=False,
        help=(
            "Email address to send along with requests to OpenAlex. This will make"
            " requests faster. See also "
            "https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool"
        ),
    )
    return parser
