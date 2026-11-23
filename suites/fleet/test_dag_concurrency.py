"""
NexusPilot Fleet Benchmark Suite: DAG Pipeline Scheduler & Blackboard Throughput
Evaluates complex diamond dependency resolution, barrier synchronization, and message bus throughput.
"""

import os
import sys
import time
import tempfile
from typing import Dict, Any

FLEET_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-fleet\server")
if FLEET_SERVER_DIR not in sys.path:
    sys.path.insert(0, FLEET_SERVER_DIR)

from orchestrator.dag_engine import DAGEngine
from bus.blackboard import Blackboard
from bus.db import FleetDatabase


def run_benchmark() -> Dict[str, Any]:
    print("[Fleet Benchmark] Testing DAG Pipeline Scheduling & Blackboard Throughput...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db = FleetDatabase(os.path.join(tmp_dir, "fleet_dag.db"))
        dag = DAGEngine()
        blackboard = Blackboard(db)

        # 1. Benchmark Diamond DAG Dependency Resolution
        # Topology: A -> [B, C, D] -> [E, F] -> G
        mission_id = "mission_diamond_benchmark"
        db.create_mission(mission_id=mission_id, goal="Benchmark 7-Node Diamond Pipeline")

        nodes = [
            ("task_A", "Root bootstrap", []),
            ("task_B", "Frontend worker", ["task_A"]),
            ("task_C", "Backend worker", ["task_A"]),
            ("task_D", "Database worker", ["task_A"]),
            ("task_E", "Integration tester 1", ["task_B", "task_C"]),
            ("task_F", "Integration tester 2", ["task_C", "task_D"]),
            ("task_G", "Final deploy verification", ["task_E", "task_F"]),
        ]

        for t_id, desc, deps in nodes:
            dag.add_task(task_id=t_id, title=desc, description=desc, dependencies=deps, status="PENDING")

        # Step through execution
        # Stage 0: Initial ready tasks should ONLY be task_A
        ready_0 = [t["task_id"] for t in dag.get_ready_tasks()]
        assert ready_0 == ["task_A"], f"Expected ['task_A'], got {ready_0}"

        # Complete task_A
        dag.tasks["task_A"]["status"] = "COMPLETED"

        # Stage 1: Fan-out [task_B, task_C, task_D] should now be ready
        ready_1 = sorted([t["task_id"] for t in dag.get_ready_tasks()])
        assert ready_1 == ["task_B", "task_C", "task_D"], f"Expected B,C,D, got {ready_1}"

        # Complete task_B and task_C
        dag.tasks["task_B"]["status"] = "COMPLETED"
        dag.tasks["task_C"]["status"] = "COMPLETED"
        ready_2 = sorted([t["task_id"] for t in dag.get_ready_tasks()])
        assert "task_E" in ready_2 and "task_D" in ready_2 and "task_F" not in ready_2

        # Complete task_D
        dag.tasks["task_D"]["status"] = "COMPLETED"
        ready_3 = [t["task_id"] for t in dag.get_ready_tasks()]
        assert "task_F" in ready_3

        # Complete task_E and task_F
        dag.tasks["task_E"]["status"] = "COMPLETED"
        dag.tasks["task_F"]["status"] = "COMPLETED"
        ready_4 = [t["task_id"] for t in dag.get_ready_tasks()]
        assert ready_4 == ["task_G"]

        # Complete task_G
        dag.tasks["task_G"]["status"] = "COMPLETED"
        ready_final = dag.get_ready_tasks()
        assert len(ready_final) == 0

        # Verify topological sort order
        topo_order = dag.topological_sort()
        assert topo_order.index("task_A") < topo_order.index("task_B")
        assert topo_order.index("task_B") < topo_order.index("task_E")
        assert topo_order.index("task_E") < topo_order.index("task_G")

        # 2. Benchmark Blackboard Message Bus Throughput
        iterations = 500
        t0 = time.perf_counter()
        for i in range(iterations):
            blackboard.broadcast(
                mission_id=mission_id,
                source_worker_id="coder_node",
                topic="status_update",
                content=f"Processed shard {i} with payload hash {hash(i)}"
            )
        write_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        write_throughput = (iterations / write_elapsed_ms) * 1000.0

        # Read throughput
        t0 = time.perf_counter()
        for _ in range(250):
            blackboard.query(mission_id=mission_id, topic="status_update")
        read_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        read_throughput = (250 / read_elapsed_ms) * 1000.0

        print(f"  ✓ 7-Node Diamond Pipeline Execution: PASS (Zero Deadlocks, Correct Barrier Sync)")
        print(f"  ✓ Blackboard Write Throughput: {write_throughput:,.0f} msgs/sec ({write_elapsed_ms:.2f}ms for {iterations} msgs)")
        print(f"  ✓ Blackboard Read Query Throughput: {read_throughput:,.0f} queries/sec")

        status = "PASS" if write_throughput > 150.0 else "FAIL"
        return {
            "name": "fleet_dag_concurrency",
            "dag_nodes": len(nodes),
            "dag_status": "COMPLETED",
            "blackboard_write_throughput_mps": round(write_throughput, 1),
            "blackboard_read_throughput_qps": round(read_throughput, 1),
            "status": status
        }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
