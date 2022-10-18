# ASReview Datatools

[![PyPI version](https://badge.fury.io/py/asreview-datatools.svg)](https://badge.fury.io/py/asreview-datatools) [![Downloads](https://pepy.tech/badge/asreview-datatools)](https://pepy.tech/project/asreview-datatools) ![PyPI - License](https://img.shields.io/pypi/l/asreview-datatools) ![Deploy and release](https://github.com/asreview/asreview-datatools/workflows/Deploy%20and%20release/badge.svg) ![Build status](https://github.com/asreview/asreview-datatools/workflows/test-suite/badge.svg) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6625879.svg)](https://doi.org/10.5281/zenodo.6625879)

ASReview Datatools is an extension to [ASReview
LAB](https://github.com/asreview/asreview) that can be used to:
- [**Describe**](#data-describe) basic properties of a dataset (e.g., number of papers, number of inclusions,
the amount of missing data and duplicates)
- [**Convert**](#data-convert) file formats via the command line
- [**Deduplicate**](#data-dedup) data based on properties of the data
- [**Compose**](#data-compose-experimental) a single (labeled, partly labeled, or unlabeled) dataset from multiple datasets.

ASReview datatools is available for ASReview Lab **v1.1+**.
If you are using ASReview Lab v0.x, use [ASReview-statistics](https://pypi.org/project/asreview-statistics/) instead of ASReview datatools.
---
## Installation
ASReview Datatools requires Python 3.7+ and [ASReview LAB](https://github.com/asreview/asreview) version 1.1 or later.

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

where `NAME_OF_TOOL` is the name of one of the tools below (`describe`, `convert`, `compose`, or `dedup`)
followed by positional arguments and optional arguments.

Each tool has its own help description which is available with

```bash
asreview data NAME_OF_TOOL -h
```
---
## Tools
### Data Describe

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

### Data Convert

Convert the format of a dataset. For example, convert a RIS dataset into a
CSV, Excel, or TAB dataset.

```
asreview data convert MY_DATASET.ris MY_OUTPUT.csv
```

### Data Dedup

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

### Data Compose (Experimental)
Compose is where datasets with different labels (or no labels) can be assembled into a single dataset.

❗ Compose is an experimental feature. We would love to hear your feedback. Please keep in mind that this feature can change in the future. 

#### Data format
Your data files need to be in tabular or RIS file format.
The output file and all input files should be in the same format.

- **Tabular file format:**
Supported tabular file formats are `.csv`, `.tab`, `.tsv` or `.xlsx`.
Ensure the column names adhere to the predetermined set of [accepted column names](https://asreview.readthedocs.io/en/latest/data_format.html).


- **RIS file format:**
A RIS file has `.ris` or `.txt` as an extension.
Read [how to format](https://asreview.readthedocs.io/en/latest/data_format.html) your RIS files.
ASReview converts the labeling decisions in RIS files to a binary variable: irrelevant as `0` and relevant as `1`.

Records marked as unseen or with missing labeling decisions are converted to `-1` by ASReview.

#### Run script
Assume you have records in `MY_DATASET_1.ris` from which you want to keep all existing labels
and records in `MY_DATASET_2.ris` which you want to keep unlabeled.
Both datasets can be composed into a single dataset using:
```bash
asreview data compose composed_output.ris -l MY_DATASET_1.ris -u MY_DATASET_2.ris
```
The resulting dataset is exported to `composed_output.ris`.

The output path (`composed_output.ris` in the example) should always be specified.
Optional arguments are available for:
- Input files
- Persistent identifier (PID) used for deduplication
- Resolving conflicting labels

#### Input files
Overview of possible input files and corresponding properties, use at least one of the following arguments:

| Arguments            | Action                                     |
|----------------------|--------------------------------------------|
| `--relevant`, `-r`   | Label all records from this dataset as `relevant` in the composed dataset.   |
| `--irrelevant`, `-i` | Label all records from this dataset as `irrelevant` in the composed dataset. |
| `--labeled`, `-l`    | Use existing labels from this dataset in the composed dataset.           |
| `--unlabeled`, `-u`  | Remove all labels from this dataset in the composed dataset.              |

#### Persistent identifier
Duplicate checking is based on title/abstract and a persistent identifier (PID) like the digital object identifier (DOI).
By default, `doi` is used as PID. It is possible to use the flag `--pid`  to specify a persistent identifier other than `doi`.

#### Resolving conflicting labels
Each record is marked as relevant, irrelevant, or unlabeled.
In case of a duplicate record, it may be labeled ambiguously (e.g., one record with two different labels).
`--hierarchy`/`-h` is used to specify a hierarchy of labels.
Pass the letters `r` (relevant), `i` (irrelevant), and `u` (unlabeled) in any order to set label hierarchy.
By default, the order is `riu` which means that:
- Relevant labels are prioritized over irrelevant and unlabeled.
- Irrelevant labels are prioritized over unlabeled ones.

If compose runs into conflicting labels, the user is warned, and the conflicting records are shown.
To specify what happens in case of conflicts, use the `--conflict_resolve`/`-c` flag.
This is set to `keep_one` by default, options are:

| Resolve method | Action in case of conflict                                                              |
|----------------|-----------------------------------------------------------------------------------------|
| `keep_one`     | Keep one label, using `--hierarchy` to determine which label to keep                    |
| `keep_all`     | Keep conflicting records as duplicates in the composed dataset (ignoring `--hierarchy`) | 
| `abort`        | Abort                                                                                   |

#### Example
```bash
asreview data compose composed_output.ris -l MY_DATASET_1.ris -u MY_DATASET_2.ris -o uir -c abort
```
Above command will compose a dataset from `MY_DATASET_1.ris` and `MY_DATASET_2.ris`.
The labels from `MY_DATASET_1.ris` are kept, and all records from `MY_DATASET_2.ris` are marked as unlabeled.
In case any duplicate ambiguously labeled records exist, either within a dataset or across the datasets:
- Unlabeled is prioritized over irrelevant and relevant labels.
- Irrelevant labels are prioritized over relevant labels.

If there are conflicting/contradictory labels, the user is warned, records with inconsistent labels are shown, and the script is aborted.

---

## License

This extension is published under the [MIT license](/LICENSE).

## Contact

This extension is part of the ASReview project ([asreview.ai](https://asreview.ai)). It is maintained by the
maintainers of ASReview LAB. See [ASReview
LAB](https://github.com/asreview/asreview) for contact information and more
resources.
