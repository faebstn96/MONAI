# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import unittest

import numpy as np
import torch
from parameterized import parameterized

from monai.metrics import VarianceMetric, compute_variance

_device = "cuda:0" if torch.cuda.is_available() else "cpu"

# keep background, 1D Case
TEST_CASE_1 = [  # y_pred (3, 1, 3), expected out (0.0)
    {
        "y_pred": torch.tensor([[[1.0, 1.0, 1.0]], [[1.0, 1.0, 1.0]], [[1.0, 1.0, 1.0]]], device=_device),
        "include_background": True,
        "spatial_map": False,
    },
    [[0.0]],
]

# keep background, 2D Case
TEST_CASE_2 = [  # y_pred (1, 1, 2, 2), expected out (0.0)
    {
        "y_pred": torch.tensor([[[[1.0, 1.0], [1.0, 1.0]]]], device=_device),
        "include_background": True,
        "spatial_map": False,
    },
    [[0.0]],
]

# keep background, 3D Case
TEST_CASE_3 = [  # y_pred (1, 1, 1, 2, 2), expected out (0.0)
    {
        "y_pred": torch.tensor([[[[[1.0, 1.0], [1.0, 1.0]]]]], device=_device),
        "include_background": True,
        "spatial_map": False,
    },
    [[0.0]],
]

# remove background, 1D Case
TEST_CASE_4 = [  # y_pred (3, 1, 3), expected out (0.0)
    {
        "y_pred": torch.tensor(
            [
                [[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]],
                [[4.0, 5.0, 6.0], [1.0, 1.0, 1.0]],
                [[7.0, 8.0, 9.0], [1.0, 1.0, 1.0]],
            ],
            device=_device,
        ),
        "include_background": False,
        "spatial_map": False,
    },
    [[0.0]],
]

# Spatial Map Test Case for 2D Case
TEST_CASE_5 = [  # y_pred (1, 1, 2, 2), expected out all (0.0) map of 2x2
    {
        "y_pred": torch.tensor([[[[1.0, 1.0], [1.0, 1.0]]]], device=_device),
        "include_background": True,
        "spatial_map": True,
    },
    [[0.0, 0.0], [0.0, 0.0]],
]

# Spatial Map Test Case for 3D Case
TEST_CASE_6 = [  # y_pred (1, 1, 2, 2, 2), expected out all (0.0) map of 2x2x2
    {
        "y_pred": torch.tensor([[[[[1.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 1.0]]]]], device=_device),
        "include_background": True,
        "spatial_map": True,
    },
    [[[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]]],
]

# Threshold test for a 1D Case
TEST_CASE_7 = [  # y_pred (3, 1, 3), expected out (0.0)
    {
        "y_pred": torch.tensor(
            [
                [[1.0, 2.0, 3.0], [1.0, 1.0, 0.0]],
                [[4.0, 5.0, 6.0], [1.0, 1.0, 1.0]],
                [[7.0, 8.0, 9.0], [1.0, 1.0, 0.0]],
                [[1.0, 2.0, 3.0], [1.0, 1.0, 1.0]],
            ],
            device=_device,
        ),
        "include_background": False,
        "spatial_map": False,
        "threshold": 0.001,
    },
    [[0.083167]],
]


class TestComputeVariance(unittest.TestCase):
    @parameterized.expand([TEST_CASE_1, TEST_CASE_2, TEST_CASE_3, TEST_CASE_4])
    def test_value(self, input_data, expected_value):
        result = compute_variance(**input_data)
        np.testing.assert_allclose(result.cpu().numpy(), expected_value, atol=1e-4)

    @parameterized.expand([TEST_CASE_5, TEST_CASE_6])
    def test_spatial_case(self, input_data, expected_value):
        result = compute_variance(**input_data)
        np.testing.assert_allclose(result.cpu().numpy(), expected_value, atol=1e-4)

    @parameterized.expand([TEST_CASE_7])
    def test_threshold_case(self, input_data, expected_value):
        result = compute_variance(**input_data)
        np.testing.assert_allclose(result.cpu().numpy(), expected_value, atol=1e-4)

    @parameterized.expand([TEST_CASE_1, TEST_CASE_2, TEST_CASE_3, TEST_CASE_4])
    def test_value_class(self, input_data, expected_value):
        vals = {}
        vals["y_pred"] = input_data.pop("y_pred")
        comp_var = VarianceMetric(**input_data)
        result = comp_var(**vals)
        np.testing.assert_allclose(result.cpu().numpy(), expected_value, atol=1e-4)

    @parameterized.expand([TEST_CASE_5, TEST_CASE_6])
    def test_spatial_case_class(self, input_data, expected_value):
        vals = {}
        vals["y_pred"] = input_data.pop("y_pred")
        comp_var = VarianceMetric(**input_data)
        result = comp_var(**vals)
        np.testing.assert_allclose(result.cpu().numpy(), expected_value, atol=1e-4)


if __name__ == "__main__":
    unittest.main()
