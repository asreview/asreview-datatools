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

from pprint import pprint

from asreview.config import LOGGER_EXTENSIONS
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.statistics import Statistics


class StatEntryPoint(BaseEntryPoint):
    description = "Plotting functionality for logging files produced by "\
        "ASReview."
    extension_name = "asreview-statistics"

    def __init__(self):
        from asreviewcontrib.statistics.__init__ import __version__
        super(StatEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        parser = _parse_arguments()
        args_dict = vars(parser.parse_args(argv))

        prefix = args_dict["prefix"]
        data_dirs = args_dict["data_dirs"]
        if len(args_dict["wss"]) + len(args_dict["rrf"]) == 0:
            args_dict["wss"] = [95, 100]
            args_dict["rrf"] = [5, 10]
        with Statistics.from_dirs(data_dirs, prefix=prefix) as stat:
            if len(stat.analyses) == 0:
                print(f"No log files found in {args_dict['data_dirs']}.\n"
                      f"To be detected log files have to start with '{prefix}'"
                      f" and end with one of the following: \n"
                      f"{', '.join(LOGGER_EXTENSIONS)}.")
                return
            wss_results = {f"wss_{wss}": stat.wss(wss)
                           for wss in args_dict["wss"]}
            rrf_results = {f"rrf_{rrf}": stat.rrf(rrf)
                           for rrf in args_dict["rrf"]}
            results = {**wss_results, **rrf_results}
            pprint(results)


def _parse_arguments():
    parser = argparse.ArgumentParser(prog='asreview stat')
    parser.add_argument(
        'data_dirs',
        metavar='N',
        type=str,
        nargs='+',
        help='Data directories.'
    )
    parser.add_argument(
        "--prefix",
        default="",
        help='Filter files in the data directory to only contain files'
             'starting with a prefix.'
    )
    parser.add_argument(
        "--abstract_only",
        default=False,
        action="store_true",
        help="Use after abstract screening as the inclusions/exclusions."
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
