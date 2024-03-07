from asreviewcontrib.datatools.snowballing import (
    backward_snowballing,
    forward_snowballing,
    openalex_from_doi,
)


def test_openalex_from_doi():
    dois = [
        "https://doi.org/10.1042/cs20220150",
        "https://doi.org/10.1042/bst20220734",
        "not_a_doi",
    ]

    assert openalex_from_doi(dois) == {
        "https://doi.org/10.1042/cs20220150": "https://openalex.org/W4386305682",
        "https://doi.org/10.1042/bst20220734": "https://openalex.org/W4312006214",
        "not_a_doi": None,
    }


def test_backward_snowballing():
    identifiers = [
        "https://openalex.org/W4281483266",
        "https://openalex.org/W2008620264",
    ]

    backwards_citations = backward_snowballing(identifiers)

    assert "https://openalex.org/W1864285629" in [
        field_dict["id"] for field_dict in backwards_citations[identifiers[0]]
    ]
    assert "https://openalex.org/W950821216" in [
        field_dict["id"] for field_dict in backwards_citations[identifiers[1]]
    ]


def test_forward_snowballing():
    identifiers = [
        "https://openalex.org/W4281483266",
        "https://openalex.org/W2008620264",
    ]

    forwards_citations = forward_snowballing(identifiers)

    assert "https://openalex.org/W4386305682" in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[0]]
    ]
    assert "https://openalex.org/W2124637492" in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[1]]
    ]
