import unittest

import numpy as np
from scipy import signal

from pyacdete.loudspeaker import estimate_delay


class EstimateDelayTest(unittest.TestCase):
    def test_matches_direct_cross_correlation(self):
        rng = np.random.default_rng(34)
        x = rng.standard_normal(128) + 2.0
        y = np.pad(0.5 * x, (11, 0)) - 5.0
        y += rng.normal(scale=0.05, size=y.size)

        expected_curve = signal.correlate(y - y.mean(), x - x.mean(),
                                          mode="full", method="direct")
        expected_lags = signal.correlation_lags(y.size, x.size, mode="full")
        result = estimate_delay(x, y, 8000)

        self.assertEqual(result["lag_samples"], 11)
        self.assertEqual(result["delay_seconds"], 11 / 8000)
        np.testing.assert_array_equal(result["lags_samples"], expected_lags)
        np.testing.assert_array_equal(result["correlation"], expected_curve)
        self.assertEqual(estimate_delay(y, x, 8000)["lag_samples"], -11)

    def test_selects_the_first_signed_maximum(self):
        result = estimate_delay([1, 0, -1], [-1, 0, 1], 8000)
        np.testing.assert_array_equal(result["correlation"], [1, 0, -2, 0, 1])
        self.assertEqual(result["lag_samples"], -2)

    def test_rejects_a_constant_channel(self):
        with self.assertRaisesRegex(ValueError, "nonconstant"):
            estimate_delay([0.1, 0.1, 0.1], [1, 0, -1], 8000)


if __name__ == "__main__":
    unittest.main()
