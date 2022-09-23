import pandas as pd
import numpy as np

import asreview
from asreviewcontrib.datatools.dedup import dedup


def test_dedup():
    df_dups = asreview.ASReviewData(
        pd.DataFrame({
            "title": ["a", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
            "abstract": ["lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem",
                         "lorem", "lorem"],
            "doi": ["10.1", "10.2", "10.3", "10.3", "", "", "   ", "   ", np.nan, np.nan, None, None]
        })
    )

    df_nodups = asreview.ASReviewData(
        pd.DataFrame({
            "title": ["a", "b", "d", "e", "f", "g", "h", "i", "j", "k"],
            "abstract": ["lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem"],
            "doi": ["10.1", "10.3", "", "", "   ", "   ", "", "", "", ""]
        })
    )

    assert dedup(df_dups).df.equals(df_nodups.df)
