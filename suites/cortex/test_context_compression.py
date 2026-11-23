"""
NexusPilot Cortex Benchmark Suite: Context Budget Compression
Evaluates token reduction ratio, execution latency, and lossless error stack preservation.
"""

import os
import sys
import time
from typing import Dict, Any

CORTEX_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-cortex\server")
if CORTEX_SERVER_DIR not in sys.path:
    sys.path.insert(0, CORTEX_SERVER_DIR)

from compressor import compress_output, collapse_repeated_lines, fold_stack_traces
from telemetry import estimate_token_count


def generate_massive_test_log() -> str:
    lines = [
        "[INFO] Starting full monorepo build and unit test matrix...",
        "[DEBUG] Resolving package dependency graph...",
    ]
    # Add repeated poll / build lines (300 lines)
    for i in range(300):
        lines.append(f"[PROGRESS] Building chunk-{i%20}/output.bundle.js [hash: a7b8c9d0e1]")
    # Add framework internal stack trace spam (50 frames)
    lines.append("TypeError: Cannot read properties of undefined (reading 'headers')")
    for _ in range(50):
        lines.append("    at processTicksAndRejections (node:internal/process/task_queues:95:5)")
        lines.append("    at Layer.handle [as handle_request] (F:\\App\\node_modules\\express\\lib\\router\\layer.js:95:5)")
    # Add critical project source code error line
    lines.append("    at AuthMiddleware.validateSession (F:\\App\\src\\middleware\\auth.ts:64:18)")
    lines.append("    at Router.handle (F:\\App\\src\\routes\\api.ts:22:9)")
    lines.append("[FATAL] Test runner failed with exit code 1")
    return "\n".join(lines)


def run_benchmark() -> Dict[str, Any]:
    print("[Cortex Benchmark] Testing Adaptive Context Output Compactor...")

    raw_log = generate_massive_test_log()
    raw_chars = len(raw_log)
    raw_tokens = estimate_token_count(raw_log)

    # 1. Run Cortex Adaptive Compactor
    t0 = time.perf_counter()
    compressed, metrics = compress_output(raw_log, max_chars=1500)
    cortex_time_ms = (time.perf_counter() - t0) * 1000.0

    comp_chars = len(compressed)
    comp_tokens = estimate_token_count(compressed)
    reduction_pct = metrics["reduction_pct"]

    # 2. Check diagnostic preservation (Lossless Diagnostic Integrity)
    retains_root_cause = "auth.ts:64" in compressed or "src\\middleware\\auth.ts" in compressed
    retains_error_msg = "TypeError: Cannot read properties of undefined" in compressed
    retains_exit_code = "exit code 1" in compressed

    lossless_retention = retains_root_cause and retains_error_msg and retains_exit_code

    # 3. Simulate Naive Head/Tail Truncation Baseline
    t0 = time.perf_counter()
    head = raw_log[:750]
    tail = raw_log[-750:]
    naive_truncated = f"{head}\n...[truncated]...\n{tail}"
    naive_time_ms = (time.perf_counter() - t0) * 1000.0
    naive_retains_root_cause = "auth.ts:64" in naive_truncated

    print(f"  ✓ Raw Log: {raw_chars:,} chars (~{raw_tokens:,} tokens)")
    print(f"  ✓ Cortex Compressed: {comp_chars:,} chars (~{comp_tokens:,} tokens)")
    print(f"  ✓ Token Reduction: {reduction_pct:.1f}%")
    print(f"  ✓ Cortex Latency: {cortex_time_ms:.2f}ms")
    print(f"  ✓ Diagnostic Integrity (Error + Root Cause + Exit Code): {'PASS (100% Retained)' if lossless_retention else 'FAIL'}")
    print(f"  ✓ Baseline Naive Truncation Root Cause Retained: {naive_retains_root_cause}")

    status = "PASS" if reduction_pct >= 70.0 and lossless_retention and cortex_time_ms < 15.0 else "FAIL"
    return {
        "name": "cortex_context_compression",
        "raw_tokens": raw_tokens,
        "compressed_tokens": comp_tokens,
        "reduction_pct": round(reduction_pct, 2),
        "execution_time_ms": round(cortex_time_ms, 2),
        "lossless_diagnostic_retained": lossless_retention,
        "status": status
    }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
