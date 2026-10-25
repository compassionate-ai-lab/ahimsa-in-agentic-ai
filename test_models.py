"""Checks that the companion program reproduces every number printed in
"Ahimsa in Agentic AI" (First Edition, 2026).
Run:  python -m unittest test_models.py
"""
import unittest

import models_ahimsa_in_agentic_ai as m


class TestBookNumbers(unittest.TestCase):
    def test_ch01(self):
        self.assertEqual(m.ch01_harm_vector(),
                         ((0.1, 0.2, 0.075, 0.3), [True, True, True, True]))
        self.assertEqual(m.ch01_inaction(), (False, True))

    def test_ch02(self):
        plain, guard = m.ch02_cascade()
        self.assertEqual(plain, [0.032, 0.0512, 0.0819, 0.1311, 0.2097, 0.3355])
        self.assertEqual(guard, [0.008, 0.0032, 0.0013, 0.0005, 0.0002, 0.0001])
        self.assertEqual(m.ch02_window(), (0.00667, 0.0393, 0.0133))

    def test_ch03(self):
        self.assertEqual(m.ch03_penalty(0.3), (88.0, 59.4))
        self.assertEqual(m.ch03_penalty(2.0), (20.0, 56.0))
        self.assertEqual(m.ch03_crossover(), 1.0526)
        self.assertEqual(m.ch03_penalty(2.0, 3.0), (220.0, 176.0))
        self.assertEqual(m.ch03_crossover(3.0), 3.1579)
        self.assertEqual(m.ch03_gate(), [False, True])

    def test_ch04(self):
        self.assertEqual(m.ch04_lexicographic(), (["A", "B", "C"], "C", "A", "D"))
        self.assertEqual(m.ch04_uncertainty_default(0.92), "execute")
        self.assertEqual(m.ch04_uncertainty_default(0.64), "preserve-and-escalate")

    def test_ch05(self):
        self.assertEqual(m.ch05_horizon(), (0.5111, 0.2109, 2.42, 0.83, 0.3, False, True))
        self.assertEqual(m.ch05_margin(), (True, 0.1125, False))
        self.assertEqual(m.ch05_empty_set(), ([], ["hold-and-ask", "narrow-to-urgent"]))

    def test_ch06(self):
        self.assertEqual(m.ch06_scalar_vs_vector(), (0.12, 0.35, True, False))
        rows, cols, empty = m.ch06_hazard_matrix()
        self.assertEqual(rows, {"direct": 1, "indirect": 2, "structural": 2, "neglect": 2})
        self.assertEqual(cols, {"physical": 0, "psychological": 2, "rights": 4, "integrity": 1})
        self.assertEqual(empty, 9)
        self.assertEqual(m.ch06_counterfactual(), (0.13, 0.051, 0.079))

    def test_ch07(self):
        self.assertEqual(m.ch07_cq(), [(1.5, 3.3, 0.45, 0.31, 0.7),
                                       (1.45, 0.6, 2.42, 0.71, 1.25)])
        self.assertEqual(m.ch07_minimax(), (0.9, 0.6, 0.4667, 0.5, "V"))
        self.assertEqual(m.ch07_error_weighting(), (0.1667, "grant", "deny"))

    def test_ch08(self):
        self.assertEqual(m.ch08_authority(), (400, False, 11))
        self.assertEqual(m.ch08_ledger_completeness(), (False, 1))

    def test_ch09(self):
        self.assertEqual(m.ch09_cai(), (0.62, False))
        self.assertEqual(m.ch09_cai((0.70, 0.60, 0.80, 0.70, 0.50, 0.55, 0.70)), (0.65, True))
        self.assertEqual(m.ch09_weight_attack(), (0.66, False))

    def test_ch10(self):
        self.assertEqual(m.ch10_filter(), {
            "notify-clinician": "permit", "read-public-report": "permit",
            "send-patient-summary": "reformulate", "publish-dataset": "reformulate",
            "override-device-cmd": "escalate"})
        self.assertEqual(m.ch10_path_coverage(), (0.71, 2))

    def test_ch11(self):
        self.assertEqual(m.ch11_restricted_game(), [("C", "C")])
        self.assertEqual(m.ch11_allocation(), ((2.4, 3.6), (3.0, 3.0), (0.48, 0.6)))
        self.assertEqual(m.ch11_correlated_pair(), (0.0016, 0.008512))

    def test_ch12(self):
        self.assertEqual(m.ch12_breaker(), (9, 7))
        self.assertEqual(m.ch12_degraded_capacity(), (45.0, 5.0, 0.2667))

    def test_ch13(self):
        self.assertEqual(m.ch13_exclusion(), ([400, 190, 290, 460],
                                              [0.1, 0.8636, 0.3222, 0.6571], 1340, 650))
        self.assertEqual(m.ch13_applicant_view(), (4870, 4480, 5820, 0.92, 0.77))
        self.assertEqual(m.ch13_alerts(), [9.0, 10.0])

    def test_ch14(self):
        self.assertEqual(m.ch14_stopping(), (1.29, 0.21, 1.318))
        self.assertEqual(m.ch14_stopping(latency=0.35), (1.47, 0.03, 1.216))
        self.assertEqual(m.ch14_amplification(), [1.52, 3.52])
        self.assertEqual(m.ch14_zone_floor(), ([55.0, 40.0, 5.0], [50.9, 37.1, 12.0], (0.25, 0.6)))

    def test_ch15(self):
        self.assertEqual(m.ch15_contestation(), 0.15)
        self.assertEqual(m.ch15_maturity(), (3, 4))

    def test_ch16(self):
        self.assertEqual(m.ch16_audit(), (35.3, 2500.0, 70.8, 0.62, False))
        self.assertEqual(m.ch16_near_band(), (4, 2, 4))

    def test_ch17(self):
        self.assertEqual(m.ch17_gap(), (4.48, 1.76, 2.54, 0.39))
        self.assertEqual(m.ch17_required_rate(), 1.2911)

    def test_ch18(self):
        self.assertEqual(m.ch18_floor_review(), ["PC"])
        self.assertEqual(m.ch18_commitments(), 0.6)

    def test_appendix_d(self):
        self.assertEqual(m.appendix_d_upper(), ((0.0225, 0.045, 0.06, 0.03), True))
        self.assertEqual(m.appendix_d_summary_draft(), (0.21, False))


class TestSafetyProperties(unittest.TestCase):
    """Contract tests for the componentwise gate used throughout."""

    def test_invalid_values_never_pass(self):
        caps = (0.05, 0.10, 0.10, 0.10)
        for bad in (float("nan"), float("inf"), -0.01, None, "0.01", True):
            self.assertFalse(m.within_ceilings((bad, 0.0, 0.0, 0.0), caps), bad)

    def test_missing_dimension_never_passes(self):
        self.assertFalse(m.within_ceilings((0.0, 0.0, 0.0), (0.05, 0.10, 0.10, 0.10)))
        self.assertFalse(m.within_ceilings((), ()))

    def test_filter_never_permits_a_breach(self):
        eps = (0.05, 0.10, 0.10, 0.10)
        for name, d in m.ch10_filter().items():
            if d == "permit":
                self.assertTrue(m.within_ceilings(m.TOOL_CALLS[name], eps))

    def test_uncertainty_default_validates_confidence(self):
        for bad in (None, float("nan"), float("inf"), -0.1, 1.5, "0.9", True):
            self.assertEqual(m.ch04_uncertainty_default(bad), "preserve-and-escalate", bad)
        self.assertEqual(m.ch04_uncertainty_default(1.0), "execute")
        for bad in (None, float("nan"), float("inf"), -0.1, 1.2):
            with self.assertRaises(ValueError):
                m.ch04_uncertainty_default(0.9, threshold=bad)

    def test_floor_veto_independent_of_weights(self):
        scores = (1.0, 1.0, 1.0, 1.0, 0.30, 1.0, 1.0)
        for w in ((0.2, 0.15, 0.1, 0.15, 0.15, 0.1, 0.15), (0.5, 0.1, 0.1, 0.1, 0.0, 0.1, 0.1)):
            self.assertFalse(m.ch09_cai(scores, w)[1])


if __name__ == "__main__":
    unittest.main()
