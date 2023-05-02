# Tutorials

--- 
Below are several examples to illustrate how to use `ASReview-datatools`.  Make
sure to have installed
[asreview-datatools](https://github.com/asreview/asreview-datatools) and
[ASReview LAB](https://asreview.nl/download/) v1.1 or higher.

Overview of the tutorials:
1. [Update systematic review](#update-systematic-review)
2. [Add prior knowledge](#add-prior-knowledge)
3. [Prepare a dataset for a simulation study](#prepare-a-dataset-for-a-simulation-study)


Allowed data formats are described in the [ASReview
documentation](https://asreview.readthedocs.io/en/latest/data_format.html).
ASReview converts the labeling decisions in [RIS files](https://asreview.readthedocs.io/en/latest/data_format.html#ris-file-format) to a binary variable:
irrelevant as `0` and relevant as `1`. Records marked as unseen or with
missing labeling decisions are converted to `-1`.

--- 

## Update Systematic Review 

Assume you are working on a systematic review and you want to update the
review with newly available records. The original data is stored in
`MY_LABELED_DATASET.csv` and the file contains a
[column](https://asreview.readthedocs.io/en/latest/data_labeled.html#label-format)
containing the labeling decissions. In order to update the systematic review,
you run the original  search query again but with a new date. You save the
newly found records in `SEARCH_UPDATE.ris`. 


In the command line interface (CLI), navigate to the directory where the
dataset(s) are stored:

```bash
cd Parent_directory
```

### Preparing your data

The original data and the newly found records are in a different datafile
format (CSV and RIS).  You can convert files to the same file format using the
`convert` script.  For example, to convert SEARCH_UPDATE.ris to CSV format,
open the command line interface (CLI) and navigate to the directory where the
dataset(s) are stored and run

```bash
asreview data convert SEARCH_UPDATE.ris SEARCH_UPDATE.csv
```

Duplicate records can be removed with with `dedup` script. The algorithm
removes duplicates using the Digital Object Indentifier
([DOI](https://www.doi.org/)) and the title plus abstract. 

```bash
asreview data dedup SEARCH_UPDATE.csv -o SEARCH_UPDATE_DEDUP.csv
```

### Describe input

If you want to see descriptive info on your input datasets, run these commands:

```bash
asreview data describe MY_LABELED_DATASET.csv -o MY_LABELED_DATASET_description.json
asreview data describe SEARCH_UPDATE_DEDUP.csv -o SEARCH_UPDATE_description.json
```
The results will be exported to `MY_LABELED_DATASET_description.json` and `SEARCH_UPDATE_description.json`.

### Compose datasets

Use the `compose` script to add `SEARCH_UPDATE_DEDUP.csv` to `MY_LABELED_DATASET.csv`:

```bash
asreview data compose updated_search.csv -l MY_LABELED_DATASET.csv -u SEARCH_UPDATE_DEDUP.csv
```
The flag `-l` means the labels in `MY_LABELED_DATASET.csv` will be kept.

The flag `-u` means all records from `SEARCH_UPDATE_DEDUP.csv` will be
added as unlabeled to the composed dataset. 

If a record exists in both datasets, it is assumed the record containing a
label is maintained, see the default [conflict resolving
strategy](https://github.com/asreview/asreview-datatools#resolving-conflicting-labels).
To keep both records (with and without label), use 

```bash
asreview data compose updated_search.csv -l MY_LABELED_DATASET.csv -u SEARCH_UPDATE_DEDUP.csv -c keep
```

The composed dataset will be exported to `COMPOSED_DATA.csv`.

### Describe output

To see descriptive info on the composed dataset:

```bash
asreview data describe COMPOSED_DATA.csv -o updated_search_description.json
```
The result will be exported to `updated_search_description.json`.

### Continue screening in ASReview lab

The [partly
labelled](https://asreview.readthedocs.io/en/latest/data_labeled.html#partially-labeled-data)
data, `COMPOSED_DATA.csv`, can be uploaded to [ASReview lab - Oracle
mode](https://asreview.readthedocs.io/en/latest/project_create.html). The
lables will be reckognized by ASReview and used to train the first iteration
of the model and you can continue screening all unlabeled records found in the
new search.

---
## Add prior knowledge

Assume you have just executed a search query for a systematic review and you
want to use a pre-defined set of relevant and irrelevant records as training
data. The search results are stored in `SEARCH_RESULTS.ris`, and the records
you already know to be relevant/irrelevant are saved in
`PRIOR_RELEVANT.ris` and `PRIOR_IRRELEVANT.ris` respectively.


In the command line interface (CLI), navigate to the directory where the dataset(s) are stored:
```bash
cd Parent_directory
```
### Describe input
If you want to see descriptive info on your input datasets, run these commands:
```bash
asreview data describe SEARCH_RESULTS.ris -o SEARCH_RESULTS_description.json
asreview data describe PRIOR_RELEVANT.ris -o PRIOR_RELEVANT_description.json
asreview data describe PRIOR_IRRELEVANT.ris -o PRIOR_IRRELEVANT_description.json
```

The results will be exported to `SEARCH_RESULTS_description.json`,
`PRIOR_RELEVANT_description.json` and `PRIOR_IRRELEVANT_description.json`.


### Compose datasets
To create one dataset with labels only for the training data to be used in ASREview, run:

```bash
asreview data compose search_with_priors.ris -u SEARCH_RESULTS.ris -r PRIOR_RELEVANT.ris -i PRIOR_IRRELEVANT.ris
```

The flag `-r` means all records from `PRIOR_RELEVANT.ris` will be added as
relevant records to the composed dataset.

The flag `-i` means all records from `PRIOR_IRRELEVANT.ris` will be added
as irrelevant.

The flag `-u` means all other records from `SEARCH_RESULTS.ris` will be
added as unlabeled.

If any duplicate records exist across the datasets, by default the order of
keeping labels is:
1. relevant 
2. irrelevant
3. unlabeled

You can configure the behavior in resolving conflicting labels by setting the
hierarchy differently. To do so, pass the letters r (relevant), i
(irrelevant), and u (unlabeled) in any order to, for example, `--hierarchy
uir`. 


The composed dataset will be exported to `search_with_priors.ris`.

### Describe output
To see descriptive info on the composed dataset:

```bash
asreview data describe search_with_priors.ris -o search_with_priors_description.json
```

The result will be exported to `search_with_priors_description.json` in the
output folder.


### Start screening in ASReview lab

The [partly
labelled](https://asreview.readthedocs.io/en/latest/data_labeled.html#partially-labeled-data)
data, `search_with_priors.ris`, can be uploaded to [ASReview lab - Oracle
mode](https://asreview.readthedocs.io/en/latest/project_create.html). The
lables will be reckognized by ASReview and used to train the first iteration
of the model and you can continue screening all unlabeled records found in the
new search.

---
## Prepare a dataset for a simulation study

Assume you want to use the [simulation
mode](https://asreview.readthedocs.io/en/latest/simulation_overview.html) of
ASReview but the data is not stored in one singe file containing the meta-data
and labelling decissions as required by ASReview. 

Suppose the following files are available:

- `SCREENED.ris`: all records that were screened
- `RELEVANT.ris`: the subset of relevant records after manually screening all the records.  

You need to compose the files into a single file where all records from
`RELEVANT.csv` are relevant all other records are irrelevant.

In the command line interface (CLI), navigate to the directory where the
dataset(s) are stored:

```bash
cd Parent_directory
```

### Describe input

If you want to see descriptive info on your input datasets, run these commands:

```bash
asreview data describe SCREENED.ris -o SCREENED_description.json
asreview data describe RELEVANT.ris -o RELEVANT_description.json
```
The results will be exported to `SCREENED_description.json` and `RELEVANT_description.json`.

### Compose datasets

Run `compose.py` to compose a new dataset from `SCREENED.ris` and `RELEVANT.ris`:

```bash
asreview data compose screened_with_labels.ris -i SCREENED.ris -r RELEVANT.ris
```

The flag `-r` means all records from `RELEVANT.ris` will be added as
relevant to the composed dataset.

The flag `-i` means all other records from `SCREENED.ris` will be added as
irrelevant.

The composed dataset will be exported to `screened_with_labels.ris`.

### Describe output

To see descriptive info on the composed dataset:

```bash
asreview data describe screened_with_labels.ris -o screened_with_labels_description.json
```
The result will be exported to `screened_with_labels_description.json`.

### Run simulation in ASReview lab

The resulting file `screened_with_labels.ris` can be uploaded to [ASReview lab
Simulation
mode](https://asreview.readthedocs.io/en/latest/simulation_webapp.html). This
allows you to simulate the screening procedure of the systematic review as if
it were carried out using ASReview lab.
