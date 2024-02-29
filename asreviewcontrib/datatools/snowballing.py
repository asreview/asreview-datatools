import os

import pyalex
from dotenv import load_dotenv
from pyalex import Works

load_dotenv()

# OpenAlex polite pool:
# https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool
pyalex.config.email = os.environ.get("OPENALEX_EMAIL")
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


def forwards_snowballing(identifiers: list[str]) -> dict[str, list[dict]]:
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


def backwards_snowballing(identifiers: list[str]) -> dict[str, list[dict]]:
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
