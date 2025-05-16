import time
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.latency import LatencyAnalyzer
from models.market_impact import AlmgrenChrissModel
from models.regression import SlippageModel
from utils.logger import logger

class PerformanceTest:
    def __init__(self):
        self.latency_analyzer = LatencyAnalyzer()
        self.market_impact = AlmgrenChrissModel()
        self.regression = SlippageModel()
        
    def measure_latency(self, iterations=1000):
        total_latency = 0
        latencies = []
        
        print("\nLatency Test Results:")
        print("-" * 50)
        
        for i in range(iterations):
            start_time = time.perf_counter()
            # Simulate processing load
            self.market_impact.calculate_market_impact(100000, 50.0, 0.1, 100.0)
            end_time = time.perf_counter()
            
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
            total_latency += latency
            
        avg_latency = total_latency / iterations
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"Average Latency: {avg_latency:.3f}ms")
        print(f"Maximum Latency: {max_latency:.3f}ms")
        print(f"Minimum Latency: {min_latency:.3f}ms")
        
    def test_accuracy(self, test_cases=100):
        correct_predictions = 0
        total_error = 0
        
        print("\nAccuracy Test Results:")
        print("-" * 50)
        
        for i in range(test_cases):
            # Generate test data
            test_price = 100 + (i % 10)
            test_volume = 1000 * (i + 1)
            
            # Make prediction with realistic parameters
            predicted_impact = self.market_impact.calculate_market_impact(
                test_volume, 0.3, test_volume * 2, test_price)
            
            # Expected impact using Almgren-Chriss model components
            gamma = 0.15  # permanent impact factor
            eta = 2.0    # temporary impact factor
            expected_impact = (gamma * test_volume) + (eta * 0.3 * np.sqrt(test_volume / (test_volume * 2)))
            
            # Calculate relative error
            error = abs(predicted_impact - expected_impact) / expected_impact
            total_error += error
            
            if error < 0.10:  # Allow 10% relative error for "correct" prediction
                correct_predictions += 1
        
        accuracy = (correct_predictions / test_cases) * 100
        avg_error = total_error / test_cases
        
        print(f"Prediction Accuracy: {accuracy:.2f}%")
        print(f"Average Error: {avg_error:.6f}")

def main():
    print("Starting Performance Tests")
    print("=" * 50)
    
    tester = PerformanceTest()
    
    # Run latency tests
    tester.measure_latency()
    
    # Run accuracy tests
    tester.test_accuracy()

if __name__ == "__main__":
    main()