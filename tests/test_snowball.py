from pathlib import Path

import pandas as pd
import pyalex

from asreviewcontrib.datatools.snowball import backward_snowballing
from asreviewcontrib.datatools.snowball import forward_snowballing
from asreviewcontrib.datatools.snowball import openalex_from_doi
from asreviewcontrib.datatools.snowball import snowball

INPUT_DIR = Path(__file__).parent / "demo_data"
EMAIL = "asreview@uu.nl"

pyalex.config.email = EMAIL

# These works were chosen for testing forward snowballing.
# They have a DOI, they cite and are cited by, their cited_by_count is less than 400,
# so it takes only two requests to get all citing works. And they are from the previous
# century so the cited_by_count is unlikely to change very much.
# These are also the same records as in the demo datasets 'snowballing_doi.csv' and
# 'snowballing_openalex.csv'.
WORKS = [
    {
        "id": "https://openalex.org/W2051970045",
        "doi": "https://doi.org/10.1071/bt9750475",
        "title": "Myrmecochorous plants in Australia and their dispersal by ants",
        "cited_by_count": 372,
        "cited_by": "https://openalex.org/W2174650845",
        "cites": "https://openalex.org/W1538725992",
    },
    {
        "id": "https://openalex.org/W104454400",
        "doi": "https://doi.org/10.1007/bf00699039",
        "title": (
            "Mimicking the one-dimensional marginal distributions of processes having"
            " an ito differential"
        ),
        "cited_by_count": 299,
        "cited_by": "https://openalex.org/W1842249978",
        "cites": "https://openalex.org/W1513091520",
    },
]


def test_openalex_from_doi():
    dois = [
        "https://doi.org/10.1042/cs20220150",
        "https://doi.org/10.1042/bst20220734",
        "not_a_doi",
    ]

    assert openalex_from_doi(dois) == {
        "10.1042/cs20220150": "https://openalex.org/W4386305682",
        "10.1042/bst20220734": "https://openalex.org/W4312006214",
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
    identifiers = [work["id"] for work in WORKS]

    forwards_citations = forward_snowballing(identifiers)

    assert WORKS[0]["cited_by"] in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[0]]
    ]
    assert WORKS[1]["cited_by"] in [
        field_dict["id"] for field_dict in forwards_citations[identifiers[1]]
    ]


def test_openalex_id_forward(tmpdir):
    out_fp = Path(tmpdir, "forward.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=out_fp,
        forward=True,
        backward=False,
        use_all=False,
        email=EMAIL,
    )
    df = pd.read_csv(out_fp)
    assert len(df) >= 364

    all_out_fp = Path(tmpdir, "forward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=all_out_fp,
        forward=True,
        backward=False,
        use_all=True,
        email=EMAIL,
    )
    df_all = pd.read_csv(all_out_fp)
    assert len(df_all) >= 656


def test_openalex_id_backward(tmpdir):
    out_fp = Path(tmpdir, "backward.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=out_fp,
        forward=False,
        backward=True,
        use_all=False,
        email=EMAIL,
    )
    df = pd.read_csv(out_fp)
    assert len(df) == 40

    all_out_fp = Path(tmpdir, "backward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=all_out_fp,
        forward=False,
        backward=True,
        use_all=True,
        email=EMAIL,
    )
    df_all = pd.read_csv(all_out_fp)
    assert len(df_all) == 45


def test_snowballing_from_doi(tmpdir):
    out_fp = Path(tmpdir, "doi_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_doi.csv",
        output_path=out_fp,
        forward=False,
        backward=True,
        use_all=True,
        email=EMAIL,
    )
    df = pd.read_csv(out_fp)
    assert len(df) == 45
