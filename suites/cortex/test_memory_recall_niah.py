"""
NexusPilot Cortex Benchmark Suite: Needle-In-A-Haystack (NIAH) Memory Retrieval
Evaluates multi-session long-term memory retrieval accuracy, recall, and search latency.
"""

import os
import sys
import time
import tempfile
from typing import Dict, Any, List

CORTEX_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-cortex\server")
if CORTEX_SERVER_DIR not in sys.path:
    sys.path.insert(0, CORTEX_SERVER_DIR)

from memory import MemoryStore, MemoryDatabase


def run_benchmark() -> Dict[str, Any]:
    print("[Cortex Benchmark] Testing Needle-In-A-Haystack (NIAH) Recall & Latency...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "benchmark_niah.db")
        db = MemoryDatabase(db_path)
        store = MemoryStore(db)

        # 1. Populate 100 realistic distractor memories across typical dev environments
        distractor_topics = ["kubernetes", "aws", "docker", "redis", "kafka", "elasticsearch", "nginx", "monitoring"]
        for i in range(100):
            topic = distractor_topics[i % len(distractor_topics)]
            fact = f"The {topic} deployment node-{i} is configured with replica_count={i%4+1} in us-east-{i%2+1}"
            store.record_manual_fact(fact, subject=f"infra_{topic}_{i}", category="architecture")

        # 2. Inject 15 distinct needles spanning preferences, constraints, architectures, and credentials
        needles = [
            ("Always use pnpm and never run npm or yarn", "pnpm package manager preference", "package_manager", "preference"),
            ("Database connection pool size must be set to 64 for PostgreSQL", "PostgreSQL database connection pool size", "postgres_pool", "architecture"),
            ("Production API tokens are managed via HashiCorp Vault enterprise", "HashiCorp Vault secret storage", "vault_secrets", "security" if hasattr(store, 'categories') else "architecture"),
            ("Frontend framework is VitePress with Vue 3 components", "VitePress frontend framework", "frontend_stack", "architecture"),
            ("Never commit .env files to any Git repository", "Git security commit rule", "git_security", "constraint"),
            ("Redis cluster timeout is configured at 250 milliseconds", "Redis cluster timeout configuration", "redis_timeout", "architecture"),
            ("Integration tests require docker-compose up -d before running", "Integration test execution command", "integration_tests", "preference"),
            ("Staging server domain is staging.api.internal.net", "staging API server domain", "staging_domain", "architecture"),
            ("Log level in production must be set to WARN", "production log level setting", "prod_log_level", "preference"),
            ("All public API responses must conform to JSON:API v1.1 format", "JSON:API response specification format", "api_format", "constraint"),
            ("Docker base image must be alpine:3.19 for microservices", "Docker base image alpine", "docker_base", "architecture"),
            ("Branch naming convention must follow feature/jira-key-short-desc", "Git branch naming convention rule", "git_branching", "constraint"),
            ("Webhook endpoint secret is rotated every 30 days automatically", "Webhook endpoint secret rotation", "webhook_security", "architecture"),
            ("Payment gateway uses Stripe API version 2024-06-20", "Stripe payment gateway API version", "stripe_version", "architecture"),
            ("Kubernetes ingress controller is Traefik v3.1", "Kubernetes ingress controller Traefik", "ingress_controller", "architecture"),
        ]

        for fact, _, subj, cat in needles:
            store.record_manual_fact(fact, subject=subj, category=cat if cat in ("preference", "architecture", "constraint") else "architecture")

        # 3. Execute Needle Retrieval Queries
        latencies = []
        hits = 0
        for needle_fact, query, _, _ in needles:
            t0 = time.perf_counter()
            retrieved = store.search_relevant_memories(query, limit=5)
            dt_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(dt_ms)

            # Match criteria: check if needle fact snippet is in retrieved items
            target_snippet = needle_fact[:25].lower()
            found = any(target_snippet in r["fact"].lower() for r in retrieved)
            if found:
                hits += 1

        recall_pct = (hits / len(needles)) * 100.0
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"  ✓ Total Memories in Store: 100 distractors + {len(needles)} needles")
        print(f"  ✓ Recall Accuracy: {recall_pct:.1f}% ({hits}/{len(needles)} found in top-5)")
        print(f"  ✓ Retrieval Latency: Avg: {avg_latency:.2f}ms | P95: {p95_latency:.2f}ms")

        status = "PASS" if recall_pct >= 90.0 and avg_latency < 25.0 else "FAIL"
        return {
            "name": "cortex_niah_memory_retrieval",
            "distractors": 100,
            "needles": len(needles),
            "recall_pct": round(recall_pct, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "status": status
        }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
