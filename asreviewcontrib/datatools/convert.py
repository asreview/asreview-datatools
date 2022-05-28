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

from asreview.data import ASReviewData
from asreview.entry_points import BaseEntryPoint


class DataConvertEntryPoint(BaseEntryPoint):
    description = "Convert file formats like RIS, CSV, and Excel for use in ASReview."
    extension_name = "asreview-datatools"

    def __init__(self):
        from asreviewcontrib.datatools.__init__ import __version__
        super(DataConvertEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        parser = _parse_arguments(
            version=f"{self.extension_name}: {self.version}")
        args = parser.parse_args(argv)

        # read data in ASReview data object
        asdata = ASReviewData.from_file(args.input_path)

        asdata.to_file(args.output_path)


def _parse_arguments(version="Unknown"):
    parser = argparse.ArgumentParser(prog="asreview datatools")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("output_path", type=str, help="The file path of the dataset.")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version,
    )

    return parser
