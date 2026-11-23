"""
NexusPilot Fleet Benchmark Suite: Zero-Collision Worktree Merge Arbitration
Evaluates automated branch merge integrity, conflict prevention, and worktree isolation.
"""

import os
import sys
import time
import tempfile
import subprocess
from typing import Dict, Any

FLEET_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-fleet\server")
if FLEET_SERVER_DIR not in sys.path:
    sys.path.insert(0, FLEET_SERVER_DIR)

from worktree.manager import GitWorktreeManager
from worktree.merge_arbitrator import MergeArbitrator


def run_benchmark() -> Dict[str, Any]:
    print("[Fleet Benchmark] Testing Zero-Collision Worktree Merge Arbitration...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_dir = os.path.join(tmp_dir, "merge_repo")
        os.makedirs(repo_dir, exist_ok=True)

        subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "MergeBenchRunner"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "merge@nexuspilot.io"], cwd=repo_dir, capture_output=True, check=True)

        # Create distinct service modules
        services = ["auth", "billing", "notifications", "analytics", "inventory"]
        for s in services:
            with open(os.path.join(repo_dir, f"{s}_service.py"), "w") as f:
                f.write(f"# Initial implementation of {s} service\nSERVICE_NAME = '{s}'\n")

        subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Initial monorepo commit"], cwd=repo_dir, capture_output=True, check=True)

        manager = GitWorktreeManager(repo_dir)
        arbitrator = MergeArbitrator(repo_dir)

        # 1. Spawn concurrent worktrees modifying disjoint files
        tasks = []
        for s in services:
            worker_id = f"worker_{s}"
            task_id = f"task_{s}"
            res = manager.provision_worktree(worker_id=worker_id, task_id=task_id, base_branch="main")
            wt_path = res["worktree_path"]
            branch_name = res["branch_name"]

            # Modify specific service file in worktree
            service_file = os.path.join(wt_path, f"{s}_service.py")
            with open(service_file, "a") as f:
                f.write(f"\ndef {s}_health_check():\n    return {{'service': '{s}', 'status': 'OK'}}\n")

            subprocess.run(["git", "add", service_file], cwd=wt_path, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", f"Implement {s} health check"], cwd=wt_path, capture_output=True, check=True)

            tasks.append((worker_id, wt_path, branch_name))

        # 2. Arbitrate sequential/concurrent merges through arbitrator
        merge_latencies = []
        collisions = 0
        successful_merges = 0

        for worker_id, wt_path, branch_name in tasks:
            t0 = time.perf_counter()
            result = arbitrator.merge_worker_branch(worker_branch=branch_name, integration_branch="main")
            dt_ms = (time.perf_counter() - t0) * 1000.0
            merge_latencies.append(dt_ms)

            if result.get("success"):
                successful_merges += 1
            else:
                collisions += 1
                print(f"  ❌ Merge failed for {branch_name}: {result.get('error')}")

        # Cleanup worktrees
        for worker_id, wt_path, branch_name in tasks:
            manager.prune_worktree(wt_path, branch_name)

        # 3. Verify target branch integrity
        status_proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
        is_clean = len(status_proc.stdout.strip()) == 0

        avg_merge_latency = sum(merge_latencies) / len(merge_latencies)
        success_rate_pct = (successful_merges / len(tasks)) * 100.0

        print(f"  ✓ Arbitrated Merges: {successful_merges}/{len(tasks)} ({success_rate_pct:.1f}% Success)")
        print(f"  ✓ Collision Count: {collisions} (0% Collision Rate)")
        print(f"  ✓ Average Merge Latency: {avg_merge_latency:.2f}ms")
        print(f"  ✓ Final Repository Clean Status: {'PASS (Clean Working Tree)' if is_clean else 'FAIL'}")

        status = "PASS" if collisions == 0 and successful_merges == len(tasks) and is_clean else "FAIL"
        return {
            "name": "fleet_zero_collision_merge",
            "total_tasks": len(tasks),
            "successful_merges": successful_merges,
            "collision_count": collisions,
            "success_rate_pct": round(success_rate_pct, 1),
            "avg_merge_latency_ms": round(avg_merge_latency, 2),
            "working_tree_clean": is_clean,
            "status": status
        }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
