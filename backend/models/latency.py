import time
from typing import Dict, List, Optional

class LatencyAnalyzer:
    def __init__(self):
        self.measurements: List[float] = []
        self.stats: Dict[str, float] = {}

    def measure(self, operation: str) -> float:
        start = time.monotonic()
        return start

    def complete_measurement(self, start_time: float, operation: str) -> float:
        end = time.monotonic()
        latency = end - start_time
        self.measurements.append(latency)
        return latency

    def get_statistics(self) -> Dict[str, float]:
        if not self.measurements:
            return {}
        self.stats = {
            'min': min(self.measurements),
            'max': max(self.measurements),
            'avg': sum(self.measurements) / len(self.measurements)
        }
        return self.stats

    def reset(self) -> None:
        self.measurements.clear()
        self.stats.clear()

def measure_latency(func):
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Latency: {end - start:.6f} seconds")
        return result
    return wrapper
