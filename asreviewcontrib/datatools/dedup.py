import re
from argparse import Namespace
from difflib import SequenceMatcher

import ftfy
import pandas as pd
from asreview import ASReviewData
from rich.console import Console
from rich.text import Text
from tqdm import tqdm


def _print_similar_list(similar_list: list[tuple[int, int]], data: pd.Series) -> None:
    print_seq_matcher = SequenceMatcher()
    console = Console()
    print('Found similar titles at lines:')

    for i, j in similar_list:
        print_seq_matcher.set_seq1(data.iloc[i])
        print_seq_matcher.set_seq2(data.iloc[j])
        text = Text()
        text.append(f"\nLines {i+1} and {j+1}:\n", style='bold')

        for tag, i1, i2, j1, j2 in print_seq_matcher.get_opcodes():
            if tag == 'replace':
                # add rich strikethrough
                text.append(f'{data.iloc[i][i1:i2]}', style='red strike')
                text.append(f'{data.iloc[j][j1:j2]}', style='green')
            if tag == 'delete':
                text.append(f'{data.iloc[i][i1:i2]}', style='red strike')
            if tag == 'insert':
                text.append(f'{data.iloc[j][j1:j2]}', style='green')
            if tag == 'equal':
                text.append(f'{data.iloc[i][i1:i2]}', style='dim')

        console.print(text)

    print('')


def drop_duplicates_by_similarity(
        asdata: ASReviewData,
        similarity: float = 0.98,
        skip_abstract: bool = False,
        discard_stopwords: bool = False,
        stopwords_language: str = 'english',
        strict_similarity: bool = False,
        verbose: bool = False) -> None:

    if skip_abstract:
        data = asdata.df['title']
    else:
        data = pd.Series(asdata.texts)

    symbols_regex = re.compile(r'[^ \w\d\-_]')
    spaces_regex = re.compile(r'\s+')

    s = (
        data
        .apply(ftfy.fix_text)
        .str.replace(symbols_regex, '', regex=True)
        .str.replace(spaces_regex, ' ', regex=True)
        .str.lower()
        .str.strip()
        .replace("", None)
    )

    if discard_stopwords:
        try:
            from nltk.corpus import stopwords
            stopwords_set = set(stopwords.words(stopwords_language))
        except LookupError:
            import nltk
            nltk.download('stopwords')
            stopwords_set = set(stopwords.words(stopwords_language))

        stopwords_regex = re.compile(rf'\b{"\\b|\\b".join(stopwords_set)}\b')
        s = s.str.replace(stopwords_regex, '', regex=True)

    duplicated = [False] * len(s)
    seq_matcher = SequenceMatcher()

    if verbose:
        similar_list = []
    else:
        similar_list = None

    for i, text in tqdm(s.items(), total=len(s), desc="Deduplicating"):
        seq_matcher.set_seq2(text)

        for j, t in s.iloc[i+1:][abs(s.str.len() - len(text)) < 5].items():
            seq_matcher.set_seq1(t)

            if seq_matcher.real_quick_ratio() > similarity and \
                seq_matcher.quick_ratio() > similarity and \
                (not strict_similarity or seq_matcher.ratio() > similarity):

                if verbose and not duplicated[j]:
                    similar_list.append((i, j))

                duplicated[j] = True

    if verbose:
        _print_similar_list(similar_list, data)

    asdata.df = asdata.df[~pd.Series(duplicated)].reset_index(drop=True)


def deduplicate_data(asdata: ASReviewData, args: Namespace) -> None:
    initial_length = len(asdata.df)

    if args.pid not in asdata.df.columns:
        print(
            f"Not using {args.pid} for deduplication "
            "because there is no such data."
        )

    if not args.similar:
        if args.verbose:
            before_dedup = asdata.df.copy()

            # retrieve deduplicated ASReview data object
            asdata.drop_duplicates(pid=args.pid, inplace=True, reset_index=False)
            duplicate_entries = before_dedup[~before_dedup.index.isin(asdata.df.index)]

            if len(duplicate_entries) > 0:
                print("Duplicate entries:")

                if args.pid in duplicate_entries.columns:
                    for i, row in duplicate_entries.iterrows():
                        print(f"\tLine {i} - {args.pid} "
                              f"{row[args.pid]} - {row['title']}")
                else:
                    for i, row in duplicate_entries.iterrows():
                        print(f"\tLine {i} - {row['title']}")

            asdata.df.reset_index(drop=True, inplace=True)

        else:
            # retrieve deduplicated ASReview data object
            asdata.drop_duplicates(pid=args.pid, inplace=True)

    else:
        drop_duplicates_by_similarity(
            asdata,
            args.threshold,
            args.title_only,
            args.stopwords,
            args.stopwords_language,
            args.strict,
            args.verbose,
            )

    # count duplicates
    n_dup = initial_length - len(asdata.df)

    if args.output_path:
        asdata.to_file(args.output_path)
        print(
            f"Removed {n_dup} duplicates from dataset with"
            f" {initial_length} records."
        )
    else:
        print(
            f"Found {n_dup} duplicates in dataset with"
            f" {initial_length} records."
        )
