# ASReview-statistics

![Deploy and release](https://github.com/asreview/asreview-statistics/workflows/Deploy%20and%20release/badge.svg)![Build status](https://github.com/asreview/asreview-statistics/workflows/test-suite/badge.svg)

ASReview extension for generating statistics on state files and datasets.

## General

Install the package with:

```bash
pip install asreview-statistics
```
The general usage of the package is to inspect files related to the systematic review done
with ASReview. It can be used to inspect your dataset that you would like to review (or have
reviewed).

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
************  PTSD_VandeSchoot_18.csv  ************

Number of papers:            5782
Number of inclusions:        38 (0.66%)
Number of exclusions:        5744 (99.34%)
Number of unlabeled:         0 (0.00%)
Average title length:        101
Average abstract length:     1339
Average number of keywords:  8.8
Number of missing titles:    64 (of which 0 included)
Number of missing abstracts: 747 (of which 0 included)
```

Your dataset should be in a format that is readable by the ASReview software. Documentation
on how to create such a dataset is in the main project.

## State files

Another use is the quick analysis of either one state file, or multiple state files in the same
directory:

```bash
asreview stat path_to_your_state_files
```

This will give output similar to:

```
************  ptsd_nb  *******************

-----------  general  -----------
Number of runs            : 16
Number of papers          : 5782
Number of included papers : 38
Number of excluded papers : 5744
Number of unlabeled papers: 0
Number of queries         : 233

-----------  settings  -----------
model             : nb
query_strategy    : max_random
balance_strategy  : double
feature_extraction: tfidf
n_instances       : 25
n_prior_included  : 1
n_prior_excluded  : 1
mode              : simulate
model_param       : {'alpha': 3.822}
query_param       : {'strategy_1': 'max', 'strategy_2': 'random', 'mix_ratio': 0.95}
feature_param     : {}
balance_param     : {'a': 2.155, 'alpha': 0.94, 'b': 0.789, 'beta': 1.0}
abstract_only     : False

-----------  WSS/RRF  -----------
WSS@95 : 91.50 %
WSS@100: 87.56 %
RRF@5  : 97.30 %
RRF@10 : 97.64 %

```

Currently, the amount of information displayed is growing; help and suggestions are welcome!
