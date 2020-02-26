# ASReview-statistics

ASReview extension for generating statistics on log files and datasets.

## General

Install the package with:

```bash
pip install asreview-statistics
```
The general usage of the package is to inspect files related to the systematic review done with ASReview. It can be used to inspect your dataset that you would like to review (or have reviewed).

General usage:

```bash
asreview stat path_to_file
```

## Datasets

Use the following command on your command line:

```bash
asreview stat path_to_your_dataset
```

It should give some general properties of the dataset, e.g.:
```
Number of papers:            5077
Number of inclusions:        40 (0.79%)
Number of exclusions:        5037 (99.21%)
Number of unlabeled:         0 (0.00%)
Average title length:        104
Average abstract length:     1536
Number of missing titles:    0 (of which 0 included)
Number of missing abstracts: 6 (of which 0 included)
```

Your dataset should be in a format that is readable by the ASReview software. Documentation on how to create such a dataset is in the main project.

## Log files

Another use is the quick analysis of either one log file, or multiple log files in the same directory:

```bash
asreview stat path_to_your_log_files
```

This will give output similar to:
```
{'rrf_10': {'ptsd_nb': 97.63513513513513},
 'rrf_5': {'ptsd_nb': 97.2972972972973},
 'wss_100': {'ptsd_nb': 87.56055363321799},
 'wss_95': {'ptsd_nb': 91.50273543439634}}
```

Multiple log files/directories are accepted. Currently, the amount of information displayed is limited, help/suggestions are welcome!
