from datetime import datetime, time
import unittest

import co2_ampel

class Test(unittest.TestCase):

    def test_map_value(self):
        self.assertEqual(co2_ampel.map_value(0, 0, 1, 10, 20), 10)
        self.assertEqual(co2_ampel.map_value(2, 1, 3, -2, -6), -4)

    def test_map_value_clamp(self):
        self.assertEqual(co2_ampel.map_value_clamp(0, 10, 11, -10, 10), -10)

    def test_force_non_negative(self):
        self.assertEqual(co2_ampel.force_non_negative(-10), 0)
        self.assertEqual(co2_ampel.force_non_negative(10), 10)

    def test_estimate_needed_power(self):
        self.assertEqual(co2_ampel.estimate_needed_power(time(12), 60, 20), 70)
        self.assertEqual(co2_ampel.estimate_needed_power(time(0), 60, 20), 50)

unittest.main()