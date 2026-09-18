"""Jev System One Classifier."""
import os
import httpx
from dotenv import load_dotenv
from app.models import TaskType, RoutingTier, ClassificationResult

load_dotenv()

SYSTEM_ONE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

ROLES_CRITERIA = {
    TaskType.DETERMINISTIC_RULE.value: "정규식, 텍스트 파싱, 단위 변환, 단순 수식 계산 등 코드로 100% 확정 가능한 작업",
    TaskType.JEV_STRUCTURED.value: "정답지-문제 번호 연결, 역할 분류, 앵커 매칭 등 구조적이고 좁은 선택 판단 작업",
    TaskType.VISION_OCR.value: "도형, 그래프, 그림, 심하게 깨진 글리프 판독 등 시각적 인식이 필수적인 작업",
    TaskType.COMPLEX_REASONING.value: "긴 글 창작, 복잡한 코드 작성, 전략 수립 등 깊은 추론(System Two)이 필요한 작업"
}

class JevClassifier:
    """Classifies user tasks using TypeSafe Jev System One model."""

    def __init__(self, api_key: str | None = None, timeout: float = 15.0):
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")
        self.timeout = timeout

    async def classify(self, prompt: str) -> ClassificationResult:
        """Classify task and calculate matching rate."""
        if not self.api_key:
            # Offline heuristic fallback
            return self._heuristic_fallback(prompt, rationale="TYPESAFE_API_KEY not provided; heuristic fallback applied.")

        payload = {
            "model": "jev-latest",
            "state": {
                "user_prompt": prompt,
                "length": len(prompt)
            },
            "questions": {
                "task_type": {
                    "type": "choice",
                    "instructions": (
                        "사용자의 요청 텍스트를 분석하여 가장 적합한 작업 유형을 고르세요. "
                        "단순 정형 작업은 deterministic_rule, 좁은 텍스트 매칭은 jev_structured, "
                        "시각 정보는 vision_ocr, 심층 논리/코드 창작은 complex_reasoning입니다."
                    ),
                    "criteria": ROLES_CRITERIA
                },
                "can_handle_locally": {
                    "type": "noul",
                    "instructions": (
                        "이 요청이 비싼 대형 파운데이션 LLM(Gemini/Claude/GPT) 없이 "
                        "로컬 규칙 또는 저비용 Jev 판별만으로 빠르고 안전하게 처리 가능합니까?"
                    )
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(SYSTEM_ONE_ENDPOINT, json=payload, headers=headers)
            
        if not response.is_success:
            # Graceful fallback on API error
            return self._heuristic_fallback(prompt, rationale=f"Jev API returned HTTP {response.status_code}; heuristic fallback applied.")

        data = response.json()
        answers = data.get("answers", {})
        
        task_choice = answers.get("task_type", {})
        selected_type_str = task_choice.get("choice", TaskType.UNKNOWN.value)
        type_conf = float(task_choice.get("confidence", 0.5))

        noul_choice = answers.get("can_handle_locally", {})
        local_noul = float(noul_choice.get("noul", 0.5))

        # Calculate composite matching rate
        matching_rate = round(type_conf * local_noul, 4)

        # Determine Tier
        try:
            task_type = TaskType(selected_type_str)
        except ValueError:
            task_type = TaskType.UNKNOWN

        if matching_rate >= 0.70 and task_type == TaskType.DETERMINISTIC_RULE:
            recommended_tier = RoutingTier.TIER_1_LOCAL_RULE
            rationale = f"높은 일치율({matching_rate:.1%})로 로컬 규칙 엔진에서 즉시 처리 가능합니다."
        elif matching_rate >= 0.50 and task_type in (TaskType.DETERMINISTIC_RULE, TaskType.JEV_STRUCTURED):
            recommended_tier = RoutingTier.TIER_2_JEV_DECISION
            rationale = f"구조적 판별 작업으로 Jev System One({matching_rate:.1%})에서 초고속 저비용 처리가 권장됩니다."
        else:
            recommended_tier = RoutingTier.TIER_3_FOUNDATION_LLM
            rationale = f"작업 복잡도 또는 낮은 로컬 적합도({matching_rate:.1%})로 인해 파운데이션 LLM으로 에스컬레이션합니다."

        return ClassificationResult(
            prompt=prompt,
            task_type=task_type,
            type_confidence=type_conf,
            can_handle_locally=local_noul,
            matching_rate=matching_rate,
            recommended_tier=recommended_tier,
            rationale=rationale,
            raw_response=data
        )

    def _heuristic_fallback(self, prompt: str, rationale: str) -> ClassificationResult:
        """Fast offline heuristic if API is unavailable."""
        lower = prompt.lower()
        if any(w in lower for w in ["계산", "변환", "정규식", "더하기", "빼기", "format"]):
            task_type = TaskType.DETERMINISTIC_RULE
            matching_rate = 0.85
            tier = RoutingTier.TIER_1_LOCAL_RULE
        elif any(w in lower for w in ["매칭", "연결", "분류", "정답지", "쪽수"]):
            task_type = TaskType.JEV_STRUCTURED
            matching_rate = 0.75
            tier = RoutingTier.TIER_2_JEV_DECISION
        elif any(w in lower for w in ["그림", "사진", "그래프", "도형", "ocr", "이미지"]):
            task_type = TaskType.VISION_OCR
            matching_rate = 0.20
            tier = RoutingTier.TIER_3_FOUNDATION_LLM
        else:
            task_type = TaskType.COMPLEX_REASONING
            matching_rate = 0.15
            tier = RoutingTier.TIER_3_FOUNDATION_LLM

        return ClassificationResult(
            prompt=prompt,
            task_type=task_type,
            type_confidence=0.8,
            can_handle_locally=matching_rate,
            matching_rate=matching_rate,
            recommended_tier=tier,
            rationale=rationale
        )
