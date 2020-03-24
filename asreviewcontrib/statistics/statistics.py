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

from collections import OrderedDict

import numpy as np

from asreview.analysis.analysis import Analysis
from asreview import ASReviewData
from asreview.utils import pretty_format
from asreview.config import LABEL_NA


class StateStatistics():
    def __init__(self, path, wss_vals=[], rrf_vals=[], prefix="result"):
        self.wss_vals = wss_vals
        self.rrf_vals = rrf_vals
        self.analysis = Analysis.from_path(path, prefix=prefix)

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.analysis.close()

    @classmethod
    def from_path(cls, path, *args, prefix="", **kwargs):
        stat_inst = cls(path, *args, prefix=prefix, **kwargs)
        return stat_inst

    def wss(self, WSS_value, result_format="percentage"):
        return self.analysis.wss(WSS_value, x_format=result_format)[0]

    def rrf(self, RRF_value, result_format="percentage"):
        return self.analysis.rrf(RRF_value, x_format=result_format)[0]

    @property
    def general(self):
        n_queries = [state.n_queries()
                     for state in self.analysis.states.values()]
        return {
            "n_queries": n_queries,
            "n_states": self.analysis.num_runs,
            "n_papers": len(self.analysis.labels),
            "n_included": sum(self.analysis.labels == 1),
            "n_excluded": sum(self.analysis.labels == 0),
            "n_unlabeled": sum(self.analysis.labels == LABEL_NA)
        }

    @property
    def settings(self):
        return self.analysis.states[self.analysis._first_file].settings

    def to_dict(self):
        return {
            "settings": self.settings,
            "wss": {wss_at: self.wss(wss_at) for wss_at in self.wss_vals},
            "rrf": {rrf_at: self.rrf(rrf_at) for rrf_at in self.rrf_vals},
            "general": self.general
        }

    def __str__(self):
        results = self.to_dict()
        stat_str = "************{name:*<30}\n\n".format(
            name=f"  {self.analysis.key}  ")
        stat_str += "-----------  general  -----------\n"
        general_dict = OrderedDict({
            "Number of runs": results['general']['n_states'],
            "Number of papers": results['general']['n_papers'],
            "Number of included papers": results['general']['n_included'],
            "Number of excluded papers": results['general']['n_excluded'],
            "Number of unlabeled papers": results['general']['n_unlabeled']
        })

        n_query_list = np.array(results['general']['n_queries'])
        if np.all(np.array(n_query_list) == n_query_list[0]):
            general_dict["Number of queries"] = n_query_list[0]
        else:
            avg = np.average(n_query_list)
            minim = np.min(n_query_list)
            maxim = np.max(n_query_list)
            tstr = f"{avg} (min: {minim}, max: {maxim})"
            general_dict["Number of queries"] = tstr

        stat_str += pretty_format(general_dict)
        stat_str += f"\n"
        stat_str += "-----------  settings  -----------\n"
        stat_str += str(results["settings"]) + "\n"

        if len(results["wss"]) + len(results["rrf"]) > 0:
            stat_str += "-----------  WSS/RRF  -----------\n"
            for wss_at, wss_val in results["wss"].items():
                if wss_val is not None:
                    wss_val_str = f"{wss_val:.2f}"
                else:
                    wss_val_str = "NA"
                stat_str += f"WSS@{wss_at: <3}: {wss_val_str: <5} %\n"
            for rrf_at, rrf_val in results["rrf"].items():
                if rrf_val is not None:
                    rrf_val_str = f"{rrf_val:.2f}"
                else:
                    rrf_val_str = "NA"
                stat_str += f"RRF@{rrf_at: <3}: {rrf_val_str: <5} %\n"

        return stat_str


class DataStatistics():
    def __init__(self, data_fp):
        self.as_data = ASReviewData.from_file(data_fp)
        self.title = self.as_data.title
        self.abstract = self.as_data.abstract
        self.labels = self.as_data.labels
        self.keywords = self.as_data.keywords
        if self.labels is None:
            self.labels = np.full(len(self.as_data), LABEL_NA)

    @classmethod
    def from_file(cls, data_fp):
        return cls(data_fp)

    def n_papers(self):
        return len(self.as_data)

    def n_included(self):
        if self.labels is not None:
            return len(np.where(self.labels == 1)[0])
        return None

    def n_excluded(self):
        if self.labels is None:
            return None
        return len(np.where(self.labels == 0)[0])

    def n_unlabeled(self):
        if self.labels is None:
            return None
        return len(self.labels) - self.n_included() - self.n_excluded()

    def n_missing_title(self):
        n_missing = 0
        if self.title is None:
            return None, None
        if self.labels is None:
            n_missing_included = None
        else:
            n_missing_included = 0
        for i in range(len(self.title)):
            if len(self.title[i]) == 0:
                n_missing += 1
                if (self.labels is not None
                        and self.labels[i] == 1):
                    n_missing_included += 1
        return n_missing, n_missing_included

    def n_missing_abstract(self):
        n_missing = 0
        if self.abstract is None:
            return None, None
        if self.labels is None:
            n_missing_included = None
        else:
            n_missing_included = 0

        for i in range(len(self.abstract)):
            if len(self.abstract[i]) == 0:
                n_missing += 1
                if (self.labels is not None
                        and self.labels[i] == 1):
                    n_missing_included += 1

        return n_missing, n_missing_included

    def title_length(self):
        if self.title is None:
            return None
        avg_len = 0
        for i in range(len(self.title)):
            avg_len += len(self.title[i])
        return avg_len/len(self.title)

    def abstract_length(self):
        if self.abstract is None:
            return None
        avg_len = 0
        for i in range(len(self.abstract)):
            avg_len += len(self.abstract[i])
        return avg_len/len(self.abstract)

    def num_keywords(self):
        if self.keywords is None:
            return None
        return np.average([len(keywords) for keywords in self.keywords])

    def to_dict(self):
        n_missing_title, n_missing_title_included = self.n_missing_title()

        n_missing_abs, n_missing_abs_included = self.n_missing_abstract()
        return {
            "n_papers": self.n_papers(),
            "n_included": self.n_included(),
            "n_excluded": self.n_excluded(),
            "n_unlabeled": self.n_unlabeled(),
            "n_missing_title": n_missing_title,
            "n_missing_title_included": n_missing_title_included,
            "n_missing_abstract": n_missing_abs,
            "n_missing_abstract_included": n_missing_abs_included,
            "title_length": self.title_length(),
            "abstract_length": self.abstract_length(),
            "n_keywords": self.num_keywords(),
        }

    def format_summary(self):
        summary = self.to_dict()
        if summary['n_keywords'] is not None:
            avg_keywords = f"{summary['n_keywords']:.1f}"
        else:
            avg_keywords = None
        summary_str = (
            f"Number of papers:            {summary['n_papers']}\n"
            f"Number of inclusions:        {summary['n_included']} "
            f"({100*summary['n_included']/summary['n_papers']:.2f}%)\n"
            f"Number of exclusions:        {summary['n_excluded']} "
            f"({100*summary['n_excluded']/summary['n_papers']:.2f}%)\n"
            f"Number of unlabeled:         {summary['n_unlabeled']} "
            f"({100*summary['n_unlabeled']/summary['n_papers']:.2f}%)\n"
            f"Average title length:        {summary['title_length']:.0f}\n"
            f"Average abstract length:     {summary['abstract_length']:.0f}\n"
            f"Average number of keywords:  {avg_keywords}\n"
            f"Number of missing titles:    {summary['n_missing_title']}"
        )
        if summary['n_missing_title_included'] is not None:
            summary_str += (f" (of which {summary['n_missing_title_included']}"
                            " included)")
        summary_str += (f"\nNumber of missing abstracts: "
                        f"{summary['n_missing_abstract']}")
        if summary['n_missing_abstract_included'] is not None:
            val = summary['n_missing_abstract_included']
            summary_str += (f" (of which {val} included)")
        summary_str += "\n"
        return summary_str
