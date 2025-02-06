import re
from difflib import SequenceMatcher

import ftfy
import pandas as pd
from asreview import ASReviewData
from pandas.api.types import is_object_dtype
from pandas.api.types import is_string_dtype
from rich.console import Console
from rich.text import Text
from tqdm import tqdm


def _print_similar_list(
    similar_list: list[tuple[int, int]],
    data: pd.Series,
    pid: str,
    pids: pd.Series = None,
) -> None:
    print_seq_matcher = SequenceMatcher()
    console = Console()

    if pids is not None:
        print(f"Found similar titles or same {pid} at lines:")
    else:
        print("Found similar titles at lines:")

    for i, j in similar_list:
        print_seq_matcher.set_seq1(data.iloc[i])
        print_seq_matcher.set_seq2(data.iloc[j])
        text = Text()

        if pids is not None:
            text.append(f"\nLines {i + 1} and {j + 1} ", style="bold")
            if pids.iloc[i] == pids.iloc[j]:
                text.append(f'(same {pid} "{pids.iloc[i]}"):\n', style="dim")
            else:
                text.append(
                    f'({pid} "{pids.iloc[i]}" and "{pids.iloc[j]}"):\n', style="dim"
                )

        else:
            text.append(f"\nLines {i + 1} and {j + 1}:\n", style="bold")

        for tag, i1, i2, j1, j2 in print_seq_matcher.get_opcodes():
            if tag == "replace":
                # add rich strikethrough
                text.append(f"{data.iloc[i][i1:i2]}", style="red strike")
                text.append(f"{data.iloc[j][j1:j2]}", style="green")
            if tag == "delete":
                text.append(f"{data.iloc[i][i1:i2]}", style="red strike")
            if tag == "insert":
                text.append(f"{data.iloc[j][j1:j2]}", style="green")
            if tag == "equal":
                text.append(f"{data.iloc[i][i1:i2]}", style="dim")

        console.print(text)

    print("")


def _drop_duplicates_by_similarity(
    asdata: ASReviewData,
    pid: str,
    threshold: float = 0.98,
    title_only: bool = False,
    stopwords_language: str = None,
    strict: bool = False,
    verbose: bool = False,
) -> None:
    if title_only:
        data = asdata.df["title"]
    else:
        data = pd.Series(asdata.texts)

    symbols_regex = re.compile(r"[^ \w\d\-_]")
    spaces_regex = re.compile(r"\s+")

    # clean the data
    s = (
        data.apply(ftfy.fix_text)
        .str.replace(symbols_regex, "", regex=True)
        .str.replace(spaces_regex, " ", regex=True)
        .str.lower()
        .str.strip()
        .replace("", None)
    )

    if stopwords_language:
        try:
            from nltk.corpus import stopwords

            stopwords_set = set(stopwords.words(stopwords_language))
        except LookupError:
            import nltk

            nltk.download("stopwords")
            stopwords_set = set(stopwords.words(stopwords_language))

        stopwords_regex = re.compile(rf"\b{'\\b|\\b'.join(stopwords_set)}\b")
        s = s.str.replace(stopwords_regex, "", regex=True)

    seq_matcher = SequenceMatcher()
    duplicated = [False] * len(s)

    if verbose:
        similar_list = []
    else:
        similar_list = None

    if pid in asdata.df.columns:
        if is_string_dtype(asdata.df[pid]) or is_object_dtype(asdata.df[pid]):
            pids = asdata.df[pid].str.strip().replace("", None)
            if pid == "doi":
                pids = pids.str.lower().str.replace(
                    r"^https?://(www\.)?doi\.org/", "", regex=True
                )

        else:
            pids = asdata.df[pid]

        for i, text in tqdm(s.items(), total=len(s), desc="Deduplicating"):
            seq_matcher.set_seq2(text)

            # loop through the rest of the data if it has the same pid or similar length
            for j, t in s.iloc[i + 1 :][
                (asdata.df[pid] == asdata.df.iloc[i][pid])
                | (abs(s.str.len() - len(text)) < 5)
            ].items():
                seq_matcher.set_seq1(t)

                # if the texts have the same pid or are similar enough,
                # mark the second one as duplicate
                if pids.iloc[i] == pids.iloc[j] or (
                    seq_matcher.real_quick_ratio() > threshold
                    and seq_matcher.quick_ratio() > threshold
                    and (not strict or seq_matcher.ratio() > threshold)
                ):
                    if verbose and not duplicated[j]:
                        similar_list.append((i, j))

                    duplicated[j] = True

        if verbose:
            _print_similar_list(similar_list, data, pid, pids)

    else:
        print(f"Not using {pid} for deduplication because there is no such data.")

        for i, text in tqdm(s.items(), total=len(s), desc="Deduplicating"):
            seq_matcher.set_seq2(text)

            # loop through the rest of the data if it has similar length
            for j, t in s.iloc[i + 1 :][abs(s.str.len() - len(text)) < 5].items():
                seq_matcher.set_seq1(t)

                # if the texts are similar enough, mark the second one as duplicate
                if (
                    seq_matcher.real_quick_ratio() > threshold
                    and seq_matcher.quick_ratio() > threshold
                    and (not strict or seq_matcher.ratio() > threshold)
                ):
                    if verbose and not duplicated[j]:
                        similar_list.append((i, j))

                    duplicated[j] = True

        if verbose:
            _print_similar_list(similar_list, data, pid)

    asdata.df = asdata.df[~pd.Series(duplicated)].reset_index(drop=True)


def deduplicate_data(
    asdata: ASReviewData,
    output_path: str = None,
    pid: str = "doi",
    similar: bool = False,
    threshold: float = 0.98,
    title_only: bool = False,
    stopwords_language: str = None,
    strict: bool = False,
    verbose: bool = False,
) -> None:
    """Deduplicate an ASReview data object.

    Parameters
    ----------
    asdata : ASReviewData
        The data object.
    output_path : str, optional
        If provided, the deduplicated data object is stored at this location. By
        default None.
    pid : str, optional
        Principal identifier to use for deduplication, by default "doi"
    similar : bool, optional
        Where to deduplicate 'similar' record. The similarity of the records is
        calculated using the `SequenceMatcher` from `difflib`. By default False.
    threshold : float, optional
        Threshold score above which two records are considered duplicate.
        By default 0.98. Only applies if `similar` is set to `True`.
    title_only : bool, optional
        Only use the title for deduplication, by default False
    stopwords_language : str, optional
        Remove stopwords from this language before deduplicating, for example 'english'.
        By default None. Only applies if `similar` is set to `True`.
    strict : bool, optional
        Use a stricter algorithm to calculate the similarity between records.
        By default False. Only applies if `similar` is set to `True`.
    verbose : bool, optional
        Get verbose output during deduplicating. By default False. Only applies if
        `similar` is set to `True`.
    """
    initial_length = len(asdata.df)

    if not similar:
        if pid not in asdata.df.columns:
            print(f"Not using {pid} for deduplication because there is no such data.")

        # retrieve deduplicated ASReview data object
        asdata.drop_duplicates(pid=pid, inplace=True)

    else:
        _drop_duplicates_by_similarity(
            asdata=asdata,
            pid=pid,
            threshold=threshold,
            title_only=title_only,
            stopwords_language=stopwords_language,
            strict=strict,
            verbose=verbose,
        )

    # count duplicates
    n_dup = initial_length - len(asdata.df)

    if output_path:
        asdata.to_file(output_path)
        print(f"Removed {n_dup} duplicates from dataset with {initial_length} records.")
    else:
        print(f"Found {n_dup} duplicates in dataset with {initial_length} records.")
