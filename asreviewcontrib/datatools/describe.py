import argparse
import json
from pathlib import Path

import asreview
from asreview.data import load_data
from asreview.data.statistics import *  # noqa

from asreviewcontrib.datatools._version import get_versions


def describe(input_path, output_path=None):

    # read data in ASReview data object
    asdata = load_data(input_path)

    # based on https://google.github.io/styleguide/jsoncstyleguide.xml
    stats = {
        "asreviewVersion": asreview.__version__,
        "apiVersion": get_versions()["version"],
        "data": {
            "items": [
                {
                    "id": "n_records",
                    "title": "Number of records",
                    "description": "The number of records in the dataset.",
                    "value": n_records(asdata)
                },
                {
                    "id": "n_relevant",
                    "title": "Number of relevant records",
                    "description": "The number of relevant records in the dataset.",
                    "value": n_relevant(asdata)
                },
                {
                    "id": "n_irrelevant",
                    "title": "Number of irrelevant records",
                    "description": "The number of irrelevant records in the dataset.",
                    "value": n_irrelevant(asdata)
                },
                {
                    "id": "n_unlabeled",
                    "title": "Number of unlabeled records",
                    "description": "The number of unlabeled records in the dataset.",
                    "value": n_unlabeled(asdata)
                },
                {
                    "id": "n_missing_title",
                    "title": "Number of records with missing title",
                    "description": "The number of records in the dataset with missing title.",
                    "value": n_missing_title(asdata)[0]
                },
                {
                    "id": "n_missing_abstract",
                    "title": "Number of records with missing abstract",
                    "description": "The number of records in the dataset with missing abstract.",
                    "value": n_missing_abstract(asdata)[0]
                },
                {
                    "id": "n_duplicates",
                    "title": "Number of duplicate records (basic algorithm)",
                    "description": "The number of duplicate records in the dataset based on similar text.",
                    "value": n_duplicates(asdata)
                }
            ]
        }
    }  # noqa

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)

    print(json.dumps(stats, indent=2))


def _parse_arguments_describe():
    parser = argparse.ArgumentParser(prog="asreview data describe")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("--output_path", "-o", default=None, type=str, help="The file path of the dataset.")

    return parser
