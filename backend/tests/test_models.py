import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.market_impact import calculate_market_impact

class TestMarketImpact(unittest.TestCase):
    def test_market_impact(self):
        result = calculate_market_impact(100, 0.02, 1000)
        self.assertGreater(result, 0)

if __name__ == "__main__":
    unittest.main()
