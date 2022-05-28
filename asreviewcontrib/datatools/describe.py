# Copyright 2020 The ASReview Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
from pathlib import Path

import asreview
from asreview.data import load_data
from asreview.data.statistics import *  # noqa
from asreview.entry_points import BaseEntryPoint


class DataDescribeEntryPoint(BaseEntryPoint):
    description = "Describe data files."
    extension_name = "asreview-datatools"

    def __init__(self):
        from asreviewcontrib.datatools.__init__ import __version__
        super(DataDescribeEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        parser = _parse_arguments(
            version=f"{self.extension_name}: {self.version}")
        args = parser.parse_args(argv)

        # read data in ASReview data object
        asdata = load_data(args.input_path)

        # based on https://google.github.io/styleguide/jsoncstyleguide.xml
        stats = {
            "asreviewVersion": asreview.__version__,
            "apiVersion": self.version,
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

        if args.output_path:
            with open(args.output_path, 'w') as f:
                json.dump(stats, f, indent=2)

        print(json.dumps(stats, indent=2))


def _parse_arguments(version="Unknown"):
    parser = argparse.ArgumentParser(prog="asreview datatools")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("--output_path", "-o", default=None, type=str, help="The file path of the dataset.")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version,
    )

    return parser
