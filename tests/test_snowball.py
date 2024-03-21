from pathlib import Path

import pandas as pd

from asreviewcontrib.datatools.snowball import backward_snowballing
from asreviewcontrib.datatools.snowball import forward_snowballing
from asreviewcontrib.datatools.snowball import openalex_from_doi
from asreviewcontrib.datatools.snowball import snowball

INPUT_DIR = Path(__file__).parent / "demo_data"


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


def test_openalex_id_forward(tmpdir):
    out_fp = Path(tmpdir, "forward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=out_fp,
        forward=True,
        backward=False,
        use_all=False,
    )
    df = pd.read_csv(out_fp)
    assert len(df) >= 23

    all_out_fp = Path(tmpdir, "forward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=all_out_fp,
        forward=True,
        backward=False,
        use_all=True,
    )
    df_all = pd.read_csv(all_out_fp)
    assert len(df_all) >= 387


def test_openalex_id_backward(tmpdir):
    out_fp = Path(tmpdir, "forward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=out_fp,
        forward=False,
        backward=True,
        use_all=False,
    )
    df = pd.read_csv(out_fp)
    assert len(df) == 31

    all_out_fp = Path(tmpdir, "backward_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_openalex.csv",
        output_path=all_out_fp,
        forward=False,
        backward=True,
        use_all=True,
    )
    df_all = pd.read_csv(all_out_fp)
    assert len(df_all) == 117


def test_snowballing_from_doi(tmpdir):
    out_fp = Path(tmpdir, "doi_all.csv")
    snowball(
        input_path=INPUT_DIR / "snowballing_doi.csv",
        output_path=out_fp,
        forward=False,
        backward=True,
        use_all=True,
    )
    df = pd.read_csv(out_fp)
    assert len(df) == 117
