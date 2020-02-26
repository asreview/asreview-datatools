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

# import matplotlib.pyplot as plt
import numpy as np

from asreview.analysis.analysis import Analysis
from asreview import ASReviewData


class LogStatistics():
    def __init__(self, path_list, prefix="result"):
        self.analyses = {}

        for path in path_list:
            new_analysis = Analysis.from_path(path, prefix=prefix)
            if new_analysis is not None:
                data_key = new_analysis.key
                self.analyses[data_key] = new_analysis

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        for analysis in self.analyses.values():
            analysis.close()

    @classmethod
    def from_paths(cls, path_list, prefix="result"):
        plot_inst = cls(path_list, prefix=prefix)
        return plot_inst

    def wss(self, WSS_value, result_format="percentage"):
        return {
            key: analysis.wss(WSS_value, x_format=result_format)[0]
            for key, analysis in self.analyses.items()
        }

    def rrf(self, RRF_value, result_format="percentage"):
        return {
            key: analysis.rrf(RRF_value, x_format=result_format)[0]
            for key, analysis in self.analyses.items()
        }


class DataStatistics():
    def __init__(self, data_fp):
        self.as_data = ASReviewData.from_file(data_fp)
        self.title = self.as_data.title
        self.abstract = self.as_data.abstract
        self.labels = self.as_data.labels

    @classmethod
    def from_file(cls, data_fp):
        return cls(data_fp)

    def n_papers(self):
        return len(self.title)

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
        if self.labels is None:
            n_missing_included = None
        else:
            n_missing_included = 0
        for i in range(len(self.title)):
            if len(self.title[i]) == 0:
                n_missing += 1
                if (self.labels is not None
                        and self.labels[i] != 0):
                    n_missing_included += 1
        return n_missing, n_missing_included

    def n_missing_abstract(self):
        n_missing = 0
        if self.labels is None:
            n_missing_included = None
        else:
            n_missing_included = 0

        for i in range(len(self.abstract)):
            if len(self.abstract[i]) == 0:
                n_missing += 1
                if (self.labels is not None
                        and self.labels[i] != 0):
                    n_missing_included += 1

        return n_missing, n_missing_included

    def title_length(self):
        avg_len = 0
        for i in range(len(self.title)):
            avg_len += len(self.title[i])
        return avg_len/len(self.title)

    def abstract_length(self):
        avg_len = 0
        for i in range(len(self.abstract)):
            avg_len += len(self.abstract[i])
        return avg_len/len(self.abstract)

    def summary(self):
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
        }

    def format_summary(self):
        summary = self.summary()
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
