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

import pandas as pd

from asreview.data import load_data
from asreview.entry_points import BaseEntryPoint


class DataDedupEntryPoint(BaseEntryPoint):
    description = "Basic deduplication algorithm for datasets."
    extension_name = "asreview-datatools"

    def __init__(self):
        from asreviewcontrib.datatools.__init__ import __version__
        super(DataDedupEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        parser = _parse_arguments(
            version=f"{self.extension_name}: {self.version}")
        args = parser.parse_args(argv)

        # read data in ASReview data object
        asdata = load_data(args.input_path)

        # get the texts and clean them
        s = pd.Series(asdata.texts) \
            .str.replace("[^A-Za-z0-9]", "", regex=True) \
            .str.lower()

        # remove the records
        asdata.df = asdata.df[~s.duplicated()]

        # count duplicates
        n_dup = len(s) - len(asdata.df)

        # export the file
        if args.output_path:
            asdata.to_file(args.output_path)
            print(f"Removed {n_dup} records from dataset with {len(s)} records.")
        else:
            print(f"Found {n_dup} records in dataset with {len(s)} records.")


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
