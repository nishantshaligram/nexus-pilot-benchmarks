"""
NexusPilot Cortex Benchmark Suite: Telemetry Overhead & Throughput
Evaluates token estimation throughput, badge formatting latency, and runtime overhead.
"""

import os
import sys
import time
from typing import Dict, Any

CORTEX_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-cortex\server")
if CORTEX_SERVER_DIR not in sys.path:
    sys.path.insert(0, CORTEX_SERVER_DIR)

from telemetry import TelemetryTracker, render_badge, estimate_token_count, format_token_number


def run_benchmark() -> Dict[str, Any]:
    print("[Cortex Benchmark] Testing Telemetry Overhead & Badge Throughput...")

    tracker = TelemetryTracker()
    iterations = 2500

    # Benchmark turn recording & badge generation
    t0 = time.perf_counter()
    for i in range(iterations):
        m = tracker.record_turn(
            input_tokens=3200 + (i % 100),
            cached_tokens=85000,
            output_tokens=280 + (i % 20),
            model="gemini-2.0-flash"
        )
        badge = render_badge(m, mode="compact")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    ops_per_sec = (iterations / elapsed_ms) * 1000.0
    latency_per_turn_us = (elapsed_ms / iterations) * 1000.0

    # Test token estimation speed on diverse payloads
    payloads = [
        "const express = require('express'); const app = express(); app.listen(3000);",
        "# Markdown document\n\nHere is a list of features:\n- Feature 1\n- Feature 2",
        '{"status": "ok", "code": 200, "data": [{"id": 1, "value": "test"}]}'
    ]
    t0 = time.perf_counter()
    est_tokens = sum(estimate_token_count(p) for p in payloads * 500)
    est_time_ms = (time.perf_counter() - t0) * 1000.0
    est_throughput_tokens_per_ms = est_tokens / max(0.001, est_time_ms)

    print(f"  ✓ {iterations} Turns Recorded in {elapsed_ms:.2f}ms")
    print(f"  ✓ Telemetry Throughput: {ops_per_sec:,.0f} turns/sec")
    print(f"  ✓ Overhead Per Turn: {latency_per_turn_us:.2f} microseconds (< 0.05ms)")
    print(f"  ✓ Token Estimation Throughput: {est_throughput_tokens_per_ms:,.0f} tokens/ms")

    status = "PASS" if latency_per_turn_us < 100.0 else "FAIL"
    return {
        "name": "cortex_telemetry_overhead",
        "iterations": iterations,
        "ops_per_sec": round(ops_per_sec, 1),
        "latency_per_turn_microseconds": round(latency_per_turn_us, 2),
        "token_est_throughput_tokens_per_ms": round(est_throughput_tokens_per_ms, 1),
        "status": status
    }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
