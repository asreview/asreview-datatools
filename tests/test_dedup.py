from argparse import Namespace
from pathlib import Path

from asreview.data import ASReviewData

from asreviewcontrib.datatools.dedup import deduplicate_data

test_dir = Path(__file__).parent
file_without_doi = Path(test_dir, "demo_data", "duplicate_data_without_doi.csv")
file_with_doi = Path(test_dir, "demo_data", "duplicate_data_with_doi.csv")


def test_dedup_without_doi(tmpdir):
    """
    Test deduplication without DOI.

    The test data contains 5 records, 1 of which is an exact duplicate.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_without_doi.csv
    Not using doi for deduplication because there is no such data.
    Found 1 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_without_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(similar=False, output_path=output_path)
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 4, "Deduplicated data should have 4 records."


def test_dedup_with_doi(tmpdir):
    """
    Test deduplication with DOI.

    The test data contains 5 records, 1 of which is an exact duplicate
    and 1 of which is a duplicate based on DOI.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_with_doi.csv
    Found 2 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_with_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(similar=False, output_path=output_path)
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 3, "Deduplicated data should have 3 records."


def test_dedup_with_similarity_without_doi(tmpdir):
    """
    Test deduplication with similarity without DOI.

    The test data contains 5 records, 1 of which is an exact duplicate
    and 1 of which is a duplicate based on similarity.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_without_doi.csv --similar \
        --threshold 0.95
    Not using doi for deduplication because there is no such data.
    Found 2 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_without_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(similar=True, output_path=output_path, threshold=0.95)
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 3, "Deduplicated data should have 3 records."


def test_dedup_with_similarity_with_doi(tmpdir):
    """
    Test deduplication with similarity with DOI.

    The test data contains 5 records, 1 of which is an exact duplicate,
    1 of which is a duplicate based on DOI, and 1 of which is a duplicate
    based on similarity.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_with_doi.csv --similar \
        --threshold 0.95
    Found 3 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_with_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(similar=True, output_path=output_path, threshold=0.95)
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 2, "Deduplicated data should have 2 records."


def test_dedup_with_similarity_without_doi_stopwords(tmpdir):
    """
    Test deduplication with similarity without DOI and removing stopwords.

    The test data contains 5 records, 1 of which is an exact duplicate,
    1 of which is a duplicate based on similarity, and 1 of which is a
    duplicate based on similarity without stopwords.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_without_doi.csv --similar \
        --threshold 0.95 --stopwords
    Not using doi for deduplication because there is no such data.
    Found 3 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_without_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(
        similar=True,
        output_path=output_path,
        threshold=0.95,
        stopwords=True,
        )
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 2, "Deduplicated data should have 2 records."


def test_dedup_with_similarity_with_doi_stopwords(tmpdir):
    """
    Test deduplication with similarity with DOI and removing stopwords.

    The test data contains 5 records, 1 of which is an exact duplicate,
    1 of which is a duplicate based on DOI, 1 of which is a duplicate
    based on similarity, and 1 of which is a duplicate based on similarity
    without stopwords.

    Same as:

    asreview data dedup tests/demo_data/duplicate_data_with_doi.csv --similar \
        --threshold 0.95 --stopwords
    Found 4 duplicates in dataset with 5 records.
    """
    data = ASReviewData.from_file(file_with_doi)
    output_path = Path(tmpdir, "test_dedup.csv")
    args = Namespace(
        similar=True,
        output_path=output_path,
        threshold=0.95,
        stopwords=True,
        )
    deduplicate_data(data, args)
    as_test = ASReviewData.from_file(output_path)

    assert len(data.df) != len(as_test.df), "Data should have been deduplicated."
    assert len(data.df) == 5, "Original data should have 5 records."
    assert len(as_test.df) == 1, "Deduplicated data should have 1 record."
