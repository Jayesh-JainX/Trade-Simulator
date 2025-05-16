import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.latency import measure_latency

@measure_latency
def benchmark_calculation():
    # Simulate a calculation
    sum([i ** 2 for i in range(10000)])

benchmark_calculation()
