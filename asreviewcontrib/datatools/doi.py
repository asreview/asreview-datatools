import re
from difflib import SequenceMatcher
from random import random
from time import sleep
from typing import Any
from urllib.parse import quote

import ftfy
import requests
from asreview import ASReviewData
from requests.exceptions import ConnectTimeout
from requests.exceptions import HTTPError
from tqdm import tqdm

_SPACES_REGEX = re.compile(r'\s+')
_SYMBOLS_REGEX = re.compile(r'[^ \w\d\-_]')
_SEQ_MATCHER = SequenceMatcher()


def _fetch_doi(
        title: str,
        authors: None | str = None,
        verbose: bool = False,
        ) -> None | dict[str, Any]:
    # https://www.crossref.org/documentation/retrieve-metadata/xml-api/retrieving-dois-by-title/
    if authors is None:
        url = f"https://api.crossref.org/works?rows=1&query.title={title}" \
              "&select=title,DOI"
    else:
        url = f"https://api.crossref.org/works?rows=1&query.title={title}" \
              "&select=title,DOI,author" \
              f"&query.bibliographic={quote(authors, safe='')}"

    response = requests.get(url)
    try:
        response.raise_for_status()

    except ConnectTimeout as e:
        if verbose:
            tqdm.write(f'Timeout for {title}.\n{e}')

        raise e

    except HTTPError as e1:
        if authors is None:
            if verbose:
                tqdm.write(f'Could not fetch doi for {title}\n{str(e1)}')

            return None

        url = f"https://api.crossref.org/works?rows=1&query.title={title}" \
                "&select=title,DOI"

        response = requests.get(url)
        try:
            response.raise_for_status()

        except ConnectTimeout as e:
            if verbose:
                tqdm.write(f'Timeout for {title}.\n{e}')

            raise e

        except HTTPError as e2:
            if verbose:
                tqdm.write(f'Could not fetch doi for {title}\n{str(e2)}')

            return None

    return response.json()


def _confirm_doi_title(
        title: str,
        title_from_api: str,
        data: dict[str, Any],
        similarity: float,
        strict_similarity: bool,
        ) -> None | str:
    clean_title = _SYMBOLS_REGEX.sub('', title.lower())
    clean_title = _SPACES_REGEX.sub(' ', clean_title)

    clean_title_from_api = _SYMBOLS_REGEX.sub('', title_from_api.lower())
    clean_title_from_api = _SPACES_REGEX.sub(' ', clean_title_from_api)

    _SEQ_MATCHER.set_seq1(clean_title)
    _SEQ_MATCHER.set_seq2(clean_title_from_api)

    if _SEQ_MATCHER.real_quick_ratio() > similarity and \
        _SEQ_MATCHER.quick_ratio() > similarity and \
        (not strict_similarity or _SEQ_MATCHER.ratio() > similarity):

        return data['message']['items'][0]['DOI']

    return None


def find_dois(
        asdata: ASReviewData,
        delay: int = 750,
        similarity: float = 0.95,
        strict_similarity: bool = False,
        verbose: bool = False) -> int:
    titles = asdata.df['title'].apply(ftfy.fix_text).str.strip()

    if 'authors' in asdata.df.columns:
        authors = asdata.df['authors'].apply(ftfy.fix_text).str.strip()
    else:
        authors = None

    delay /= 1000
    dois = []

    for i, title in enumerate(tqdm(titles, desc="Finding DOIs")):
        if 'authors' in asdata.df.columns:
            data = _fetch_doi(title, authors[i], verbose)
        else:
            data = _fetch_doi(title, None, verbose)

        if data is None:
            dois.append(None)
            continue

        try:
            title_from_api = ftfy.fix_text(data['message']['items'][0]['title'][0])

        except IndexError:
            if verbose:
                tqdm.write(f'No doi found for {title}\n{str(data)}')

            dois.append(None)
            continue

        doi = _confirm_doi_title(
            title,
            title_from_api,
            data,
            similarity,
            strict_similarity,
            )

        dois.append(doi)

        # sleep for delay + random to avoid overloading with requests
        sleep(delay + random())

    asdata.df['doi'] = dois
