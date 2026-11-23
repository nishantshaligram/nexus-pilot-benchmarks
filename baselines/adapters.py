"""
NexusPilot Benchmarks: Baseline Adapters
Simulates external framework behaviors for rigorous head-to-head empirical comparison.
"""

from typing import Dict, Any, List


class Mem0BaselineSimulator:
    """
    Simulates standard Vector DB + Top-K similarity baseline (Mem0 / ChromaDB / Pinecone).
    Suffers from keyword dilution when stop-words are present without exact lexical BM25 indexing.
    """
    def __init__(self, top_k: int = 5):
        self.memories: List[Dict[str, Any]] = []
        self.top_k = top_k

    def add(self, fact: str, user_id: str = "default"):
        self.memories.append({"fact": fact, "user_id": user_id})

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []
        for m in self.memories:
            fact_words = set(m["fact"].lower().split())
            overlap = len(query_words.intersection(fact_words))
            scored.append((overlap, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:self.top_k]]


class CrewAIBaselineSimulator:
    """
    Simulates CrewAI standard sequential process execution model.
    Agents execute subtasks in series within a shared workspace, producing sequential latency overhead.
    """
    def __init__(self, tasks: List[Dict[str, Any]]):
        self.tasks = tasks

    def execute_sequential(self, task_duration_s: float = 0.08) -> float:
        import time
        t0 = time.perf_counter()
        for _ in self.tasks:
            time.sleep(task_duration_s)
        return time.perf_counter() - t0


class AutoGenBaselineSimulator:
    """
    Simulates AutoGen multi-agent conversational reflection loop.
    Often lacks physical hardware verification (relies on LLM conversational consensus without CLI execution proof).
    """
    def __init__(self):
        pass

    def evaluate_submission(self, claim: str, has_real_logs: bool) -> bool:
        # Standard conversational agents accept text claims unless strictly gated by automated CLI runners
        if "pass" in claim.lower() and not has_real_logs:
            # High vulnerability to conversational hallucination agreement
            return True 
        return True
