# NexusPilot Benchmarks: Cortex & Fleet Performance Matrix

Comprehensive empirical benchmarking harness and competitive leaderboard for the **NexusPilot** AI agent suite:
- **NexusPilot Cortex**: Cognitive Telemetry, Persistent Memory Governor (NexusMem), and Adaptive Context Window Compaction.
- **NexusPilot Fleet**: Distributed Swarm Orchestration, Zero-Collision Worktree Multiplexing, DAG Scheduling, and Two-Key Triad Consensus.

---

## 📊 Benchmark Suites

### 1. NexusPilot Cortex Benchmarks
- **Needle-In-A-Haystack (NIAH) Memory Retrieval (`suites/cortex/test_memory_recall_niah.py`)**: Tests multi-session fact recall accuracy across 100+ distractors and verifies sub-25ms retrieval latency.
- **Temporal Contradiction & Supersession (`suites/cortex/test_contradiction_resolution.py`)**: Evaluates deterministic fact supersession when architectural decisions or preferences evolve over time.
- **Adaptive Context Output Compactor (`suites/cortex/test_context_compression.py`)**: Evaluates token reduction ratios (target $\ge 70\%$) on massive build/test traces while guaranteeing 100% preservation of error lines and root-cause stack traces.
- **Telemetry Overhead & Badge Throughput (`suites/cortex/test_telemetry_accuracy.py`)**: Verifies token estimation throughput ($> 100\text{k}$ turns/sec) and microsecond-level latency overhead per turn.

### 2. NexusPilot Fleet Benchmarks
- **Worktree Multiplexing Speedup (`suites/fleet/test_worktree_speedup.py`)**: Measures parallel wall-clock speedup across multi-agent task missions compared to sequential agent loops (CrewAI / AutoGen).
- **Zero-Collision Worktree Merge Arbitration (`suites/fleet/test_merge_collision.py`)**: Stresses automated branch arbitration across concurrent worktree modifications, guaranteeing 0% merge collisions on disjoint changes.
- **Two-Key Triad Consensus (`suites/fleet/test_two_key_consensus.py`)**: Measures defect escape rate and tests anti-hallucination gates by validating that Key 2 blocks unverified test claims.
- **DAG Pipeline Scheduler & Blackboard (`suites/fleet/test_dag_concurrency.py`)**: Tests complex diamond dependency topological sorting and high-throughput shared blackboard messaging.

---

## 🚀 Running Benchmarks

### Quick Start (Run All Benchmarks)
```bash
python run_all.py
```

### Run Individual Suites
```bash
# Run Cortex benchmarks
python suites/cortex/test_memory_recall_niah.py
python suites/cortex/test_context_compression.py

# Run Fleet benchmarks
python suites/fleet/test_worktree_speedup.py
python suites/fleet/test_two_key_consensus.py
```

### Generate Leaderboard
```bash
python reports/generate_leaderboard.py
```
Outputs the leaderboard table to `reports/LEADERBOARD.md`.
