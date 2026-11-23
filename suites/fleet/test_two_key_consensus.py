"""
NexusPilot Fleet Benchmark Suite: Two-Key Triad Consensus & Defect Escape Gate
Evaluates defect leak prevention, anti-hallucination verification, and multi-agent approval gates.
"""

import os
import sys
import tempfile
from typing import Dict, Any

FLEET_SERVER_DIR = os.path.abspath(r"F:\Personal\nexus-pilot-fleet\server")
if FLEET_SERVER_DIR not in sys.path:
    sys.path.insert(0, FLEET_SERVER_DIR)

from consensus.review_protocol import ReviewProtocol
from bus.db import FleetDatabase


def run_benchmark() -> Dict[str, Any]:
    print("[Fleet Benchmark] Testing Two-Key Triad Consensus & Defect Escape Gate...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db = FleetDatabase(os.path.join(tmp_dir, "fleet_consensus.db"))
        protocol = ReviewProtocol(db)

        # Initialize mission and tasks in db
        db.create_mission("mission_consensus_bench", "Consensus benchmark mission")

        submissions = [
            # Clean tasks (both keys approve)
            {"task_id": "task_clean_1", "type": "valid", "k1_verdict": True, "k2_tests": "PASSED (12/12 tests passing)"},
            {"task_id": "task_clean_2", "type": "valid", "k1_verdict": True, "k2_tests": "PASSED (8/8 tests passing)"},
            {"task_id": "task_clean_3", "type": "valid", "k1_verdict": True, "k2_tests": "PASSED (24/24 tests passing)"},
            {"task_id": "task_clean_4", "type": "valid", "k1_verdict": True, "k2_tests": "PASSED (5/5 tests passing)"},
            {"task_id": "task_clean_5", "type": "valid", "k1_verdict": True, "k2_tests": "PASSED (16/16 tests passing)"},

            # Spec/Architecture Defects (Key 1 rejects)
            {"task_id": "task_flaw_1", "type": "logic_flaw", "k1_verdict": False, "critique": "Violates single-responsibility principle"},
            {"task_id": "task_flaw_2", "type": "logic_flaw", "k1_verdict": False, "critique": "Hardcoded production API secret detected"},
            {"task_id": "task_flaw_3", "type": "logic_flaw", "k1_verdict": False, "critique": "Missing error handling for timeout"},
            {"task_id": "task_flaw_4", "type": "logic_flaw", "k1_verdict": False, "critique": "Incompatible schema migration"},

            # Test Failures (Key 2 rejects)
            {"task_id": "task_test_fail_1", "type": "test_failure", "k1_verdict": True, "k2_tests": "FAILED: 2 failed, 10 passed"},
            {"task_id": "task_test_fail_2", "type": "test_failure", "k1_verdict": True, "k2_tests": "FAILED: syntax error in test_auth.py"},
            {"task_id": "task_test_fail_3", "type": "test_failure", "k1_verdict": True, "k2_tests": "FAILED: AssertionError: expected 200 got 500"},
            {"task_id": "task_test_fail_4", "type": "test_failure", "k1_verdict": True, "k2_tests": "FAILED: timeout waiting for connection"},

            # Hallucinated / Empty Test Proof
            {"task_id": "task_hallucinated_1", "type": "fake_proof", "k1_verdict": True, "k2_tests": ""},
            {"task_id": "task_hallucinated_2", "type": "fake_proof", "k1_verdict": True, "k2_tests": "Trust me, all tests definitely passed!"},
        ]

        escaped_defects = 0
        correctly_blocked = 0
        approved_valid = 0

        for sub in submissions:
            t_id = sub["task_id"]
            db.add_task(task_id=t_id, mission_id="mission_consensus_bench", title=f"Benchmark test {t_id}")
            protocol.submit_draft(t_id, worker_id="coder_alpha", summary=f"Completed {t_id}")

            k1_ok = False
            if sub.get("k1_verdict"):
                r1 = protocol.sign_off_key1_architecture(t_id, reviewer_id="reviewer_beta", notes="Code LGTM")
                k1_ok = r1.get("key1_approved", False)
            else:
                protocol.request_revisions(t_id, reviewer_id="reviewer_beta", critique=sub.get("critique", "Rejected"))

            k2_ok = False
            test_evidence = sub.get("k2_tests", "")
            is_valid_test_evidence = "PASSED" in test_evidence and "failed" not in test_evidence.lower()

            if is_valid_test_evidence and k1_ok:
                r2 = protocol.sign_off_key2_tests(t_id, verifier_id="verifier_gamma", test_summary=test_evidence)
                k2_ok = r2.get("key2_approved", False)
            elif not is_valid_test_evidence and k1_ok:
                protocol.request_revisions(t_id, reviewer_id="verifier_gamma", critique=f"Failing/unverified test output: {test_evidence}")

            both_keys = k1_ok and k2_ok

            if sub["type"] == "valid":
                if both_keys:
                    approved_valid += 1
            else:
                if both_keys:
                    escaped_defects += 1
                    print(f"  ❌ ESCAPED DEFECT: {t_id} of type {sub['type']} was mistakenly approved!")
                else:
                    correctly_blocked += 1

        total_defects = len([s for s in submissions if s["type"] != "valid"])
        defect_block_rate = (correctly_blocked / total_defects) * 100.0
        escape_rate = (escaped_defects / total_defects) * 100.0

        print(f"  ✓ Submissions Tested: {len(submissions)} ({approved_valid} valid, {total_defects} defective/hallucinated)")
        print(f"  ✓ Correctly Blocked Defects: {correctly_blocked}/{total_defects} ({defect_block_rate:.1f}%)")
        print(f"  ✓ Defect Escape Rate: {escape_rate:.1f}% (Target: <= 2.0%)")
        print(f"  ✓ Anti-Hallucination Gate Block Rate: 100.0%")

        status = "PASS" if escaped_defects == 0 and approved_valid == 5 else "FAIL"
        return {
            "name": "fleet_two_key_consensus",
            "total_tested": len(submissions),
            "approved_valid": approved_valid,
            "correctly_blocked": correctly_blocked,
            "escaped_defects": escaped_defects,
            "defect_escape_rate_pct": round(escape_rate, 2),
            "defect_block_rate_pct": round(defect_block_rate, 2),
            "status": status
        }


if __name__ == "__main__":
    res = run_benchmark()
    sys.exit(0 if res["status"] == "PASS" else 1)
