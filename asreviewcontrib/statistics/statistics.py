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
# import numpy as np

from asreview.analysis.analysis import Analysis


class Statistics():
    def __init__(self, data_dirs, prefix="result"):
        self.analyses = {}

        for data_dir in data_dirs:
            new_analysis = Analysis.from_dir(data_dir, prefix=prefix)
            if new_analysis is not None:
                data_key = new_analysis.key
                self.analyses[data_key] = new_analysis

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        for analysis in self.analyses.values():
            analysis.close()

    @classmethod
    def from_dirs(cls, data_dirs, prefix="result"):
        plot_inst = cls(data_dirs, prefix=prefix)
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
