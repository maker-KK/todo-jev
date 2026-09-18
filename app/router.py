"""Task Router and Execution Dispatcher."""
import time
from typing import Any
from app.classifier import JevClassifier
from app.models import ClassificationResult, RoutingTier

class TaskRouter:
    """Routes tasks to Tier 1, Tier 2, or Tier 3 handlers based on Jev classification."""

    def __init__(self, classifier: JevClassifier | None = None):
        self.classifier = classifier or JevClassifier()

    async def route_and_execute(self, prompt: str) -> dict[str, Any]:
        """Classify the prompt and dispatch to appropriate tier."""
        start_time = time.perf_counter()
        
        # Step 1: Classify with Jev
        classification: ClassificationResult = await self.classifier.classify(prompt)
        classification_time = (time.perf_counter() - start_time) * 1000

        # Step 2: Dispatch based on recommended tier
        execution_start = time.perf_counter()
        if classification.recommended_tier == RoutingTier.TIER_1_LOCAL_RULE:
            result = self._execute_tier_1_rule(prompt, classification)
        elif classification.recommended_tier == RoutingTier.TIER_2_JEV_DECISION:
            result = self._execute_tier_2_jev(prompt, classification)
        else:
            result = self._execute_tier_3_llm(prompt, classification)

        execution_time = (time.perf_counter() - execution_start) * 1000
        total_time = (time.perf_counter() - start_time) * 1000

        return {
            "prompt": prompt,
            "classification": classification.model_dump(),
            "execution": result,
            "latency_ms": {
                "classification": round(classification_time, 2),
                "execution": round(execution_time, 2),
                "total": round(total_time, 2),
            },
            "cost_tier": classification.recommended_tier.value
        }

    def _execute_tier_1_rule(self, prompt: str, classification: ClassificationResult) -> dict[str, Any]:
        """Fast local deterministic rule execution."""
        return {
            "status": "completed",
            "tier": "Tier 1 (Deterministic Rule Engine)",
            "message": "Processed locally with zero API token cost.",
            "output": f"Rule-based output for: {prompt}"
        }

    def _execute_tier_2_jev(self, prompt: str, classification: ClassificationResult) -> dict[str, Any]:
        """Low-cost Jev System One structured execution."""
        return {
            "status": "completed",
            "tier": "Tier 2 (Jev System One)",
            "message": "Processed via low-cost structured choice/noul evaluation ($0.042/M tokens).",
            "output": f"Jev-structured decision bound for: {prompt}"
        }

    def _execute_tier_3_llm(self, prompt: str, classification: ClassificationResult) -> dict[str, Any]:
        """Escalated to Foundation LLM (Gemini/Claude/GPT)."""
        return {
            "status": "escalated",
            "tier": "Tier 3 (Foundation LLM)",
            "message": "Escalated to frontier LLM for deep reasoning / code generation / vision analysis.",
            "output": f"Foundation LLM prompt payload prepared for: {prompt}"
        }
