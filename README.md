# ASReview-datatools

[![PyPI version](https://badge.fury.io/py/asreview-datatools.svg)](https://badge.fury.io/py/asreview-datatools) [![Downloads](https://pepy.tech/badge/asreview-datatools)](https://pepy.tech/project/asreview-datatools) ![PyPI - License](https://img.shields.io/pypi/l/asreview-datatools) ![Deploy and release](https://github.com/asreview/asreview-datatools/workflows/Deploy%20and%20release/badge.svg) ![Build status](https://github.com/asreview/asreview-datatools/workflows/test-suite/badge.svg) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4672242.svg)](https://doi.org/10.5281/zenodo.4672242)

ASReview-datatools is an extension to [ASReview
LAB](https://github.com/asreview/asreview) that can be used for describing
basic properties of a dataset (e.g., number of papers, number of inclusions,
the amount of missing data and duplicates), converting file formats via the
command line, and cleaning your (input) data by removing duplicate records.

❣️ ASReview-datatools is the successor to
[ASReview-statistics](https://pypi.org/project/asreview-statistics/). ASReview
datatools is available for version 1 or later. Use ASReview statistics for
versions 0.x.

## Installation

The ASReview-datatools extensions requires Python 3.7+ and [ASReview
LAB](https://github.com/asreview/asreview) version 1 or later.

The easiest way to install the datatools extension is to install from PyPI:

``` bash
pip install asreview-datatools
```

After installation of the datatools extension, `asreview` should automatically
detect it. Test this with the following command:

```bash
asreview --help
```

The extension is successfully installed if it lists `asreview data`.

## Getting started

ASReview-datatools is a command line tool that extends ASReview LAB. Each
subsection below describes one of the tools. The structure is

```bash
asreview data NAME_OF_TOOL
```

where `NAME_OF_TOOL` is the name of one of the tools below (i.e., `describe`)
followed by positional arguments and optional arguments.

Each tool has its own help description which is available with

```bash
asreview data NAME_OF_TOOL -h
```

### `data describe`

Describe the content of a dataset

```bash
asreview data describe MY_DATASET.csv
```

Export the results to a file (`output.json`)

```bash
asreview data describe MY_DATASET.csv -o output.json
```

Describe the `van_de_schoot_2017` dataset from the [benchmark
platform](https://github.com/asreview/systematic-review-datasets).

```bash
asreview data describe benchmark:van_de_schoot_2017 -o output.json
```

```
{
  "asreviewVersion": "1.0",
  "apiVersion": "1.0",
  "data": {
    "items": [
      {
        "id": "n_records",
        "title": "Number of records",
        "description": "The number of records in the dataset.",
        "value": 6189
      },
      {
        "id": "n_relevant",
        "title": "Number of relevant records",
        "description": "The number of relevant records in the dataset.",
        "value": 43
      },
      {
        "id": "n_irrelevant",
        "title": "Number of irrelevant records",
        "description": "The number of irrelevant records in the dataset.",
        "value": 6146
      },
      {
        "id": "n_unlabeled",
        "title": "Number of unlabeled records",
        "description": "The number of unlabeled records in the dataset.",
        "value": 0
      },
      {
        "id": "n_missing_title",
        "title": "Number of records with missing title",
        "description": "The number of records in the dataset with missing title.",
        "value": 5
      },
      {
        "id": "n_missing_abstract",
        "title": "Number of records with missing abstract",
        "description": "The number of records in the dataset with missing abstract.",
        "value": 764
      },
      {
        "id": "n_duplicates",
        "title": "Number of duplicate records (basic algorithm)",
        "description": "The number of duplicate records in the dataset based on similar text.",
        "value": 104
      }
    ]
  }
}
```

### `data convert`

Convert the format of a dataset. For example, convert a RIS dataset into a
CSV, Excel, or TAB dataset.

```
asreview data convert MY_DATASET.ris MY_OUTPUT.csv
```

### `data dedup`

Remove duplicate records with a simple and straightforward deduplication
algorithm (see [source
code](https://github.com/asreview/asreview-datatools/blob/master/asreviewcontrib/datatools/dedup.py)).
The algorithm concatenates the title and abstract, whereafter it removes all
non-alphanumeric tokens. Then the duplicates are removed.

```
asreview data dedup MY_DATASET.ris
```

Export the deduplicated dataset to a file (`output.csv`)

```
asreview data dedup MY_DATASET.ris -o output.csv
```

Using the `van_de_schoot_2017` dataset from the [benchmark
platform](https://github.com/asreview/systematic-review-datasets).

```
asreview data dedup benchmark:van_de_schoot_2017 -o van_de_schoot_2017_dedup.csv
```

## License

This extension is published under the [MIT license](/LICENSE).

## Contact

This extension is part of the ASReview project ([asreview.ai](https://asreview.ai)). It is maintained by the
maintainers of ASReview LAB. See [ASReview
LAB](https://github.com/asreview/asreview) for contact information and more
resources.
