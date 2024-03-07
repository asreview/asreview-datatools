import argparse
from pathlib import Path

import pandas as pd
import pyalex
from asreview import ASReviewData, load_data

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
        works_citing_id = (
            pyalex.Works().filter(cites=openalex_id).select(USED_FIELDS).get()
        )
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

    all_referenced_works = {}
    for i in range(0, len(all_identifiers), page_length):
        fltr = "|".join(all_identifiers[i : i + page_length])
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
    for identifier, ref_id_list in referenced_works.items():
        referenced_works[identifier] = [
            all_referenced_works[ref_id] for ref_id in ref_id_list
        ]
    return referenced_works


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
    id_mapping = {doi: None for doi in dois}
    for i in range(0, len(dois), page_length):
        fltr = "|".join(dois[i : i + page_length])
        for work in (
            pyalex.Works()
            .filter(doi=fltr)
            .select(["id", "doi"])
            .get(per_page=page_length)
        ):
            id_mapping[work["doi"]] = work["id"]
    return id_mapping


def snowballing(
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
    if use_all:
        data = data.df
    else:
        data = data.df.loc[data.included]

    # Add OpenAlex identifiers if not available.
    if "openalex_id" not in data.columns:
        if "doi" not in data.columns:
            raise ValueError(
                "Dataset should contain a column 'openalex_id' containing OpenAlex"
                " identifiers or a column 'doi' containing DOIs."
            )
        id_mapping = openalex_from_doi(data.doi.to_list())
        n_openalex_ids = len(
            [
                openalex_id
                for openalex_id in id_mapping.values()
                if openalex_id is not None
            ]
        )
        print(
            f"Found OpenAlex identifiers for {n_openalex_ids} out of {len(id_mapping)}"
            " records. Performing snowballing for those records."
        )
        data["openalex_id"] = [id_mapping[doi] for doi in data.doi]

    identifiers = data["openalex_id"].dropna().to_list()

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
