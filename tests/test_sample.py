# create unit tests for the sample.py file
from pathlib import Path

import pandas as pd

from asreviewcontrib.datatools.sample import sample

INPUT_DIR = Path(__file__).parent / "demo_data" / "sample_data.csv"


def test_sample(tmpdir):
    sample(INPUT_DIR, tmpdir / "output.csv", 1, "publication_year")
    df = pd.read_csv(tmpdir / "output.csv")
    assert len(df) == 3
    assert "publication_year" in df.columns
    assert df.iloc[0]["publication_year"] == 2000
    assert df.iloc[2]["publication_year"] == 2005
