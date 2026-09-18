"""Data models for Jev task classification and routing."""
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class TaskType(str, Enum):
    DETERMINISTIC_RULE = "deterministic_rule"
    JEV_STRUCTURED = "jev_structured"
    VISION_OCR = "vision_ocr"
    COMPLEX_REASONING = "complex_reasoning"
    UNKNOWN = "unknown"

class RoutingTier(str, Enum):
    TIER_1_LOCAL_RULE = "Tier 1: Local Rule Engine (0 token, <10ms)"
    TIER_2_JEV_DECISION = "Tier 2: Jev System One ($0.042/M, ~150ms)"
    TIER_3_FOUNDATION_LLM = "Tier 3: Foundation LLM Escalation ($1~$5/M, ~2000ms)"

class ClassificationResult(BaseModel):
    prompt: str
    task_type: TaskType
    type_confidence: float = Field(ge=0.0, le=1.0)
    can_handle_locally: float = Field(ge=0.0, le=1.0)
    matching_rate: float = Field(ge=0.0, le=1.0)
    recommended_tier: RoutingTier
    rationale: str
    raw_response: dict[str, Any] | None = None
