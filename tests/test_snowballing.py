from asreviewcontrib.datatools.snowballing import (
    backwards_snowballing,
    forwards_snowballing,
)


def test_backwards_snowballing():
    identifiers = [
        "https://openalex.org/W4281483266",
        "https://openalex.org/W2008620264",
    ]

    backwards_citations = backwards_snowballing(identifiers)

    assert "https://openalex.org/W1864285629" in [
        field_dict["id"] for field_dict in backwards_citations[identifiers[0]]
    ]
    assert "https://openalex.org/W950821216" in [
        field_dict["id"] for field_dict in backwards_citations[identifiers[1]]
    ]


def test_forwards_snowballing():
    identifiers = [
        "https://openalex.org/W4281483266",
        "https://openalex.org/W2008620264",
    ]

    forwards_citations = forwards_snowballing(identifiers)

    assert "https://openalex.org/W4386305682" in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[0]]
    ]
    assert "https://openalex.org/W2124637492" in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[1]]
    ]
