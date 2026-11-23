"""
NexusPilot Cortex Benchmark Suite: Temporal Contradiction & Supersession
Evaluates accuracy in updating outdated architectural decisions and resolving contradictions.
"""

import os
import sys
import time
import tempfile
from typing import Dict, Any

CORTEX_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-cortex\server")
if CORTEX_SERVER_DIR not in sys.path:
    sys.path.insert(0, CORTEX_SERVER_DIR)

from memory import MemoryStore, MemoryDatabase


def run_benchmark() -> Dict[str, Any]:
    print("[Cortex Benchmark] Testing Temporal Contradiction & Supersession...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "benchmark_contradiction.db")
        db = MemoryDatabase(db_path)
        store = MemoryStore(db)

        test_cases = [
            {
                "subject": "node_version",
                "category": "architecture",
                "old_fact": "Node.js runtime version is v18 LTS across all services",
                "new_fact": "Node.js runtime version has been upgraded to v22 LTS across all services",
                "query": "What is the Node.js runtime version?",
                "expected_key": "v22"
            },
            {
                "subject": "package_manager",
                "category": "preference",
                "old_fact": "Use yarn berry for all frontend packages",
                "new_fact": "Always use pnpm and never use yarn berry for packages",
                "query": "package manager preference rule",
                "expected_key": "pnpm"
            },
            {
                "subject": "cloud_provider",
                "category": "architecture",
                "old_fact": "Primary cloud hosting provider is AWS us-east-1",
                "new_fact": "All workloads have been migrated to Cloudflare Workers and GCP",
                "query": "current cloud hosting provider",
                "expected_key": "Cloudflare"
            }
        ]

        resolved = 0
        latencies = []

        for tc in test_cases:
            # 1. Record old fact
            store.record_manual_fact(tc["old_fact"], subject=tc["subject"], category=tc["category"])
            time.sleep(0.01) # Ensure timestamp progression

            # 2. Record new superseding fact
            store.record_manual_fact(tc["new_fact"], subject=tc["subject"], category=tc["category"])

            # 3. Query memory
            t0 = time.perf_counter()
            results = store.search_relevant_memories(tc["query"], limit=3)
            dt_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(dt_ms)

            top_fact = results[0]["fact"] if results else ""
            if tc["expected_key"].lower() in top_fact.lower():
                resolved += 1
                print(f"  ✓ [{tc['subject']}] Successfully resolved: '{top_fact}'")
            else:
                print(f"  ❌ [{tc['subject']}] Failed to resolve: Got '{top_fact}'")

        resolution_pct = (resolved / len(test_cases)) * 100.0
        avg_latency = sum(latencies) / len(latencies)

        print(f"  ✓ Contradiction Supersession Accuracy: {resolution_pct:.1f}% ({resolved}/{len(test_cases)})")
        print(f"  ✓ Query Latency: Avg: {avg_latency:.2f}ms")

        status = "PASS" if resolution_pct == 100.0 else "FAIL"
        return {
            "name": "cortex_contradiction_supersession",
            "test_cases": len(test_cases),
            "resolution_pct": round(resolution_pct, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "status": status
        }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
