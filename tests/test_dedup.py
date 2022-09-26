import pandas as pd

import asreview
from asreviewcontrib.datatools.dedup import dedup


def test_dedup():
    df_dups = asreview.ASReviewData(
        pd.DataFrame({
            "title": ["a", "a", "b", "c", "d", "e", "f", "g", "h", "i"],
            "abstract": ["lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem"],
            "doi": ["10.1", "10.2", "10.3", "10.3", "", "", "   ", "   ", None, None]
        })
    )

    df_nodups = asreview.ASReviewData(
        pd.DataFrame({
            "title": ["a", "b", "d", "e", "f", "g", "h", "i"],
            "abstract": ["lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem", "lorem"],
            "doi": ["10.1", "10.3", "", "", "   ", "   ", "", ""]
        })
    )

    pd.testing.assert_frame_equal(dedup(df_dups).df, df_nodups.df)
