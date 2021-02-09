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
import logging

from pprint import pprint

from asreview.config import LOGGER_EXTENSIONS
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.statistics import StateStatistics
from asreviewcontrib.statistics.statistics import DataStatistics
import json


class StatEntryPoint(BaseEntryPoint):
    description = "Generate statistics on datasets and ASReview state files."
    extension_name = "asreview-statistics"

    def __init__(self):
        from asreviewcontrib.statistics.__init__ import __version__
        super(StatEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        logging.getLogger().setLevel(logging.ERROR)
        version_name = f"{self.extension_name}: {self.version}"
        parser = _parse_arguments(version=version_name)
        args = vars(parser.parse_args(argv))
        output_fp = args["output"]

        log_paths = []
        stat_dict = {}

        for path in args['paths']:
            try:
                stat = DataStatistics.from_file(path)
                if output_fp is None:
                    print("************{name}************\n".format(
                        name=f"  {path}  "))
                    print(stat.format_summary(), end='')
                    print("\n")
                else:
                    stat_dict[str(path)] = stat.to_dict()
            except ValueError:
                log_paths.append(path)

        prefix = args["prefix"]
        if len(args["wss"]) + len(args["rrf"]) == 0:
            args["wss"] = [95, 100]
            args["rrf"] = [5, 10]

        for path in log_paths:
            with StateStatistics.from_path(
                    path, wss_vals=args["wss"], rrf_vals=args["rrf"],
                    prefix=prefix) as stat:
                if output_fp is None:
                    print(stat)
                else:
                    stat_dict[str(path)] = stat.to_dict()

        if output_fp is not None:
            with open(output_fp, "w") as fp:
                json.dump(stat_dict, fp, indent=2)


def _parse_arguments(version="?"):
    parser = argparse.ArgumentParser(prog='asreview stat')
    parser.add_argument(
        'paths',
        metavar='PATH',
        type=str,
        nargs='+',
        help='Data directories, data files or datasets.'
    )
    parser.add_argument(
        "-V", "--version",
        action='version',
        version=version,
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        type=str,
        help="Export the results to a JSON file."
    )
    parser.add_argument(
        "--prefix",
        default="",
        help='Filter files in the data directory to only contain files'
             'starting with a prefix.'
    )
    parser.add_argument(
        "--wss",
        default=[],
        action="append",
        help="Compute WSS @ some percentage."
    )
    parser.add_argument(
        "--rrf",
        default=[],
        action="append",
        help="Compute RRF @ some percentage."
    )
    return parser
