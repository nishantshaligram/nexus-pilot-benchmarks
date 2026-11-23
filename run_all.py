"""
NexusPilot Benchmarks: Unified Runner & Leaderboard Generator
Executes the full benchmark matrix for NexusPilot Cortex and NexusPilot Fleet,
evaluating both plugins against established industry baselines.
"""

import os
import sys
import json
import time
from typing import Dict, Any

BENCH_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BENCH_ROOT, "suites", "cortex"))
sys.path.insert(0, os.path.join(BENCH_ROOT, "suites", "fleet"))

import test_memory_recall_niah
import test_contradiction_resolution
import test_context_compression
import test_telemetry_accuracy

import test_worktree_speedup
import test_merge_collision
import test_two_key_consensus
import test_dag_concurrency


def run_full_suite() -> Dict[str, Any]:
    print("=" * 80)
    print("🌐 NEXUSPILOT UNIFIED INDUSTRY BENCHMARK HARNESS")
    print("=" * 80)

    start_time = time.time()
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cortex": {},
        "fleet": {},
        "summary": {}
    }

    # 1. Cortex Benchmarks
    print("\n" + "-" * 40)
    print("🧠 RUNNING NEXUSPILOT CORTEX BENCHMARKS")
    print("-" * 40)
    cortex_tests = [
        test_memory_recall_niah,
        test_contradiction_resolution,
        test_context_compression,
        test_telemetry_accuracy
    ]
    for test_mod in cortex_tests:
        r = test_mod.run_benchmark()
        results["cortex"][r["name"]] = r

    # 2. Fleet Benchmarks
    print("\n" + "-" * 40)
    print("⚡ RUNNING NEXUSPILOT FLEET BENCHMARKS")
    print("-" * 40)
    fleet_tests = [
        test_worktree_speedup,
        test_merge_collision,
        test_two_key_consensus,
        test_dag_concurrency
    ]
    for test_mod in fleet_tests:
        r = test_mod.run_benchmark()
        results["fleet"][r["name"]] = r

    elapsed_s = time.time() - start_time
    total_benchmarks = len(results["cortex"]) + len(results["fleet"])
    passed_count = sum(
        1 for section in (results["cortex"], results["fleet"])
        for r in section.values()
        if r.get("status") == "PASS"
    )

    results["summary"] = {
        "total_benchmarks": total_benchmarks,
        "passed": passed_count,
        "failed": total_benchmarks - passed_count,
        "elapsed_seconds": round(elapsed_s, 2),
        "status": "PASS" if passed_count == total_benchmarks else "FAIL"
    }

    print("\n" + "=" * 80)
    print(f"🏁 BENCHMARK COMPLETED: {passed_count}/{total_benchmarks} PASSED in {elapsed_s:.2f}s")
    print("=" * 80)

    # Export JSON report
    report_file = os.path.join(BENCH_ROOT, "reports", "benchmark_matrix_results.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed metrics exported to: {report_file}")

    return results


if __name__ == "__main__":
    res = run_full_suite()
    sys.exit(0 if res["summary"]["status"] == "PASS" else 1)
