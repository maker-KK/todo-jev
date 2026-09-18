"""Tests for Jev Classifier and Router."""
import pytest
from app.classifier import JevClassifier
from app.router import TaskRouter
from app.models import TaskType, RoutingTier

@pytest.mark.asyncio
async def test_offline_heuristic_fallback():
    classifier = JevClassifier(api_key=None)
    
    res1 = await classifier.classify("15 + 27 계산하고 단위 변환")
    assert res1.task_type == TaskType.DETERMINISTIC_RULE
    assert res1.recommended_tier == RoutingTier.TIER_1_LOCAL_RULE
    
    res2 = await classifier.classify("PDF 정답지 3번 문항과 쪽수 매칭 연결")
    assert res2.task_type == TaskType.JEV_STRUCTURED
    assert res2.recommended_tier == RoutingTier.TIER_2_JEV_DECISION
    
    res3 = await classifier.classify("그림에서 도형의 각도를 판독해줘")
    assert res3.task_type == TaskType.VISION_OCR
    assert res3.recommended_tier == RoutingTier.TIER_3_FOUNDATION_LLM

@pytest.mark.asyncio
async def test_router_execution():
    router = TaskRouter(classifier=JevClassifier(api_key=None))
    result = await router.route_and_execute("10 + 20 계산해줘")
    assert "latency_ms" in result
    assert result["classification"]["task_type"] == TaskType.DETERMINISTIC_RULE
