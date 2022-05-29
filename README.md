# ASReview-datatools

This package is currently under development. See [ASReview-statistics](https://pypi.org/project/asreview-statistics/) for stable version compatible with ASReview LAB <=0.19.x.

![Deploy and release](https://github.com/asreview/asreview-datatools/workflows/Deploy%20and%20release/badge.svg) ![Build status](https://github.com/asreview/asreview-datatools/workflows/test-suite/badge.svg) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4672242.svg)](https://doi.org/10.5281/zenodo.4672242)


ASReview-datatools is an extension for [ASReview
LAB](https://github.com/asreview/asreview) software. The extension can be used
for describing and cleaning your (input) data via the command line.

## Installation

The ASReview-datatools extensions requires Python 3.6+ and [ASReview
LAB](https://github.com/asreview/asreview) version 1.

The easiest way to install the datatools extension is to install from PyPI:

``` bash
pip install asreview-datatools
```

After installation of the datatools extension, `asreview` should automatically
detect it. Test this by:

```bash
asreview --help
```

If it lists `asreview data describe`, then the extension is successfully installed.

## Getting started

### `data describe`

Describe a dataset

```bash
% asreview data describe MY_DATASET.csv
```

Export the results to a file (`output.json`)

```bash
% asreview data describe MY_DATASET.csv -o output.json
```

Describe the `van_de_schoot_2017` dataset from the [benchmark
platform](https://github.com/asreview/systematic-review-datasets).

```bash
% asreview data describe benchmark:van_de_schoot_2017 -o output.json
```

```
{
  "asreviewVersion": "1.0rc2+14.gac96c1a",
  "apiVersion": "0.4+4.g3f54294",
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
algorithm. The algorithm concatenates the title and abstract, whereafter it
removes all non-alphanumeric tokens. Then the duplicates are removed.

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
asreview data dedup benchmark:van_de_schoot_2017
```

## License

This extension is MIT licensed.

## Contact

Use the issue tracker or see more contact options in the [ASReview
LAB](https://github.com/asreview/asreview) repository.
