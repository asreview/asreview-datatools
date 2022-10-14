# ASReview Datatools

[![PyPI version](https://badge.fury.io/py/asreview-datatools.svg)](https://badge.fury.io/py/asreview-datatools) [![Downloads](https://pepy.tech/badge/asreview-datatools)](https://pepy.tech/project/asreview-datatools) ![PyPI - License](https://img.shields.io/pypi/l/asreview-datatools) ![Deploy and release](https://github.com/asreview/asreview-datatools/workflows/Deploy%20and%20release/badge.svg) ![Build status](https://github.com/asreview/asreview-datatools/workflows/test-suite/badge.svg) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6625879.svg)](https://doi.org/10.5281/zenodo.6625879)

ASReview Datatools is an extension to [ASReview
LAB](https://github.com/asreview/asreview) that can be used for:
- [**Describing**](#describe) basic properties of a dataset (e.g., number of papers, number of inclusions,
the amount of missing data and duplicates)
- [**Converting**](#convert) file formats via the command line
- [**Deduplication**](#dedup): cleaning your (input) data by removing duplicate records.
- [**Composing**](#compose) datasets with different (or no) labels into a single dataset

ASReview
datatools is available for ASReview Lab **v1.1+** and requires Python 3.7+.
If you are using ASReview Lab v0.x, use [ASReview-statistics](https://pypi.org/project/asreview-statistics/) instead of ASReview datatools.
---
## Installation
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

where `NAME_OF_TOOL` is the name of one of the tools below (`describe`, `convert`, `compose` or `dedup`)
followed by positional arguments and optional arguments.

Each tool has its own help description which is available with

```bash
asreview data NAME_OF_TOOL -h
```
---
## Describe

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

<details>
  <summary>Click to see output:</summary>

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
</details>

## Convert

Convert the format of a dataset. For example, convert a RIS dataset into a
CSV, Excel, or TAB dataset.

```
asreview data convert MY_DATASET.ris MY_OUTPUT.csv
```

## Dedup

Remove duplicate records with a simple and straightforward deduplication
algorithm (see [source
code](https://github.com/asreview/asreview/blob/master/asreview/data/base.py#L453)).
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

## Compose
Compose is where datasets with different labels (or no labels) can be assembled into a single dataset.

### Data format
Your data files need to be in tabular file format or RIS file format.
All input files should use the same format.

- **Tabular file format:**
Supported tabular file formats are `.csv`, `.tab`, `.tsv` or `.xlsx`.
Make sure your column names adhere to the predetermined set of [accepted column names](https://asreview.readthedocs.io/en/latest/data_format.html).


- **RIS file format:**
RIS file formats have `.ris` or `.txt` as extension and are used by digital libraries.
Read [how to format](https://asreview.readthedocs.io/en/latest/data_format.html) your RIS files.
ASReview converts the labeling decisions in RIS files to a binary variable: irrelevant as `0` and relevant as `1`.

Records marked as unseen or with missing labeling decisions, are converted to `-1` by ASReview.

### Run script
Navigate to the directory where your data files are located:
```bash
cd Parent_directory
```
Assume you have `MY_DATASET_1.ris` from which you want to keep all existing labels
and `MY_DATASET_2.ris` which you want to mark as unlabeled. Compose into a single dataset:
```bash
asreview data compose composed_output.ris -l MY_DATASET_1.ris -u MY_DATASET_2.ris
```
The resulting dataset is exported to `composed_output.ris`.

The output path (`composed_output.ris` in the example) should always be specified.
It is followed by optional arguments for:
- Input files
- Persistent identifier (PID) used for deduplication
- Resolving conflicting labels

#### Input files
Overview of possible input files and corresponding properties, use at least one of the following arguments:

| Arguments            | Action                                     |
|----------------------|--------------------------------------------|
| `--relevant`, `-r`   | Label all records in dataset `relevant`.   |
| `--irrelevant`, `-i` | Label all records in dataset `irrelevant`. |
| `--labeled`, `-l`    | Keep existing labels in dataset.           |
| `--unlabeled`, `-u`  | Remove all labels in dataset.              |

#### Persistent identifier
Duplicate checking is based on title/abstract and a persistent identifier (PID), see [source code](https://github.com/asreview/asreview/blob/master/asreview/data/base.py#L453).
By default `doi` is used as PID, it is possible to use flag `--pid`  to specify a persistent identifier other than `doi`.

#### Resolving conflicting labels
Each record is marked as relevant, irrelevant or unlabeled.
In case of a duplicate record it is possible that it is marked ambiguously.
`--priority`/`-p` is used to specify prioritization of labels.
Pass the letters `r` (relevant), `i` (irrelevant) and `u` (unlabeled) in any order to set label prioritization order.
By default, the order is `riu` which means that:
- Relevant labels are prioritized over irrelevant and unlabeled.
- Irrelevant labels are prioritized over unlabeled.

If compose runs into any conflicts the user is warned and the conflicts are shown.
To specify what happens in case of conflicts, use the `--conflict_resolve`/`-c` flag.
This is set to `continue` by default, options are:

| Resolve method | Action in case of conflict                                                             |
|----------------|----------------------------------------------------------------------------------------|
| `continue`     | Continue, using `--priority` to determine which label to keep                          |
| `keep`         | Keep all labels for duplicate records with inconsistent labels (ignoring `--priority`) | 
| `abort`        | Abort                                                                                  |

### Example
```bash
asreview data compose composed_output.ris -l MY_DATASET_1.ris -u MY_DATASET_2.ris -o uir -c abort
```
Above command will compose a dataset from `MY_DATASET_1.ris` and `MY_DATASET_2.ris`.
The labels from `MY_DATASET_1.ris` are kept and all records from `MY_DATASET_2.ris` are marked as unlabeled.
In case any duplicate ambiguously labeled records exist, either within a dataset or across the datasets:
- Unlabeled is prioritized over irrelevant and relevant labels.
- Irrelevant labels are prioritized over relevant labels.

If there are any such conflicting/contradictory labels, the user is warned, the conflicting records are shown and the script is aborted.

### Tutorials
Several [tutorials](Tutorials.md) are available that show how compose can be used in different scenarios.

### Note
When the composed dataset is exported to RIS file format you may get a warning similar to:
```bash
C:\Python310\lib\site-packages\rispy\writer.py:114: UserWarning: label `included` not exported
warnings.warn(UserWarning(f"label `{label}` not exported"))
```
Despite the warning, the labels will still be exported, so this warning can be ignored.

---

## License

This extension is published under the [MIT license](/LICENSE).

## Contact

This extension is part of the ASReview project ([asreview.ai](https://asreview.ai)). It is maintained by the
maintainers of ASReview LAB. See [ASReview
LAB](https://github.com/asreview/asreview) for contact information and more
resources.
