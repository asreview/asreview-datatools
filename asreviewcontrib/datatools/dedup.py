import re
from difflib import Differ, SequenceMatcher
from pprint import pformat

import ftfy
import pandas as pd
from asreview import ASReviewData
from rich.console import Console
from rich.text import Text
from tqdm import tqdm


_SYMBOLS_REGEX = re.compile(r'[^ \w\d\-_]')
_SPACES_REGEX = re.compile(r'\s+')


def drop_duplicates_by_similarity(
        asdata: ASReviewData,
        similarity: float = 0.98,
        use_abstract: bool = True,
        discard_stopwords: bool = False,
        stopwords_language: str = 'english',
        verbose: bool = True):

    if use_abstract:
        data = pd.Series(asdata.texts)
    else:
        data = asdata.df['title']

    s = (
        data
        .apply(ftfy.fix_text)
        .str.replace(_SYMBOLS_REGEX, '', regex=True)
        .str.replace(_SPACES_REGEX, ' ', regex=True)
        .str.lower()
        .str.strip()
        .replace("", None)
    )

    if discard_stopwords:
        try:
            from nltk.corpus import stopwords
            STOPWORDS = set(stopwords.words(stopwords_language))
        except LookupError:
            import nltk
            nltk.download('stopwords')
            STOPWORDS = set(stopwords.words(stopwords_language))

        STOPWORDS_REGEX = re.compile(rf'\b{"\\b|\\b".join(STOPWORDS)}\b')
        s = s.str.replace(STOPWORDS_REGEX, '', regex=True)

    duplicated = (s.duplicated()) & (s.notnull())
    seq_matcher = SequenceMatcher()

    if verbose:
        similar_list = []
    else:
        similar_list = None

    for i, text in tqdm(s.items(), total=len(s), desc="Deduplicating"):
        seq_matcher.set_seq2(text)

        for j, t in s.iloc[i+1:][abs(s.str.len() - len(text)) < 5].items():
            seq_matcher.set_seq1(t)

            # could also add: and seq_matcher.ratio() > similarity:
            if seq_matcher.real_quick_ratio() > similarity and seq_matcher.quick_ratio() > similarity:
                if verbose and not duplicated[j]:
                    similar_list.append((i, j))

                duplicated[j] = True

    if verbose:
        print_seq_matcher = SequenceMatcher()
        console = Console()
        print('Found similar titles at lines')

        for i, j in similar_list:
            print_seq_matcher.set_seq1(data.iloc[i])
            print_seq_matcher.set_seq2(data.iloc[j])
            text = Text()
            text.append(f"\nLines {i} and {j}:\n", style='bold')

            for tag, i1, i2, j1, j2 in print_seq_matcher.get_opcodes():
                if tag == 'replace':
                    # add rich strikethrough
                    text.append(f'{data.iloc[i][i1:i2]}', style='strike')
                    text.append(f'{data.iloc[j][j1:j2]}')
                if tag == 'delete':
                    text.append(f'{data.iloc[i][i1:i2]}', style='strike')
                if tag == 'insert':
                    text.append(f'{data.iloc[j][j1:j2]}')
                if tag == 'equal':
                    text.append(f'{data.iloc[i][i1:i2]}', style='dim')

            console.print(str(text))

    asdata.df = asdata.df[~duplicated].reset_index(drop=True)