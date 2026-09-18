"""Jev System One Classifier with Grounded Star Skills & Preflight Guarantees."""
import os
import httpx
from dotenv import load_dotenv
from app.models import TaskType, RoutingTier, ClassificationResult
from app.config import Settings, settings as default_settings
from app.skill_registry import SkillRegistry
from app.skill_profiles import TOP_STAR_SKILL_PROFILES, StarSkillProfile

load_dotenv()

SYSTEM_ONE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

DEFAULT_ROLES_CRITERIA = {
    TaskType.DETERMINISTIC_RULE.value: "정규식, 텍스트 파싱, 단위 변환, 단순 수식 계산 등 코드로 100% 확정 가능한 작업",
    TaskType.JEV_STRUCTURED.value: "정답지-문제 번호 연결, 역할 분류, 앵커 매칭 등 구조적이고 좁은 선택 판단 작업",
    TaskType.VISION_OCR.value: "도형, 그래프, 그림, 심하게 깨진 글리프 판독 등 시각적 인식이 필수적인 작업",
    TaskType.COMPLEX_REASONING.value: "긴 글 창작, 복잡한 코드 작성, 전략 수립 등 깊은 추론(System Two)이 필요한 작업"
}

class JevClassifier:
    """Classifies user tasks using TypeSafe Jev System One model with Star Skill Grounding."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 15.0,
        settings: Settings | None = None,
        registry: SkillRegistry | None = None,
    ):
        self.settings = settings or default_settings
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")
        self.timeout = timeout
        self.registry = registry or SkillRegistry()

    def get_active_criteria(self) -> dict[str, str]:
        """Get criteria for Jev, enriched with top star skills and installed skills."""
        criteria = dict(DEFAULT_ROLES_CRITERIA)
        
        # 1. Add top curated star skills
        for sid, prof in TOP_STAR_SKILL_PROFILES.items():
            criteria[f"skill:{sid}"] = f"[{prof.domain}] {prof.summary}"

        # 2. Add other installed skills if auto-sync enabled
        if self.settings.auto_sync_skills:
            synced_skills = self.registry.build_jev_criteria(max_skills=25)
            for skill_name, skill_desc in synced_skills.items():
                k = f"skill:{skill_name}"
                if k not in criteria:
                    criteria[k] = f"[Installed Skill] {skill_desc}"

        return criteria

    async def classify(self, prompt: str) -> ClassificationResult:
        """Classify task and calculate matching rate with preflight guarantee."""
        if not self.api_key:
            return self._heuristic_fallback(prompt, rationale="TYPESAFE_API_KEY not provided; offline star-skill heuristic applied.")

        criteria = self.get_active_criteria()

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
                        "사용자의 요청 텍스트를 분석하여 가장 적합한 작업 유형 또는 스타 스킬(skill:*)을 고르세요. "
                        "단순 정형 작업은 deterministic_rule, 좁은 텍스트 매칭은 jev_structured, "
                        "시각 정보는 vision_ocr, 심층 논리/창작은 complex_reasoning입니다."
                    ),
                    "criteria": criteria
                },
                "can_handle_locally": {
                    "type": "noul",
                    "instructions": (
                        "이 요청이 비싼 대형 파운데이션 LLM 없이 로컬 규칙 또는 매칭된 특화 스킬로 처리 가능합니까?"
                    )
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(SYSTEM_ONE_ENDPOINT, json=payload, headers=headers)
        except Exception as e:
            return self._heuristic_fallback(prompt, rationale=f"Network error calling Jev API: {e}")

        if not response.is_success:
            return self._heuristic_fallback(prompt, rationale=f"Jev API returned HTTP {response.status_code}; fallback applied.")

        data = response.json()
        answers = data.get("answers", {})

        task_choice = answers.get("task_type", {})
        selected_type_str = task_choice.get("choice", TaskType.UNKNOWN.value)
        type_conf = float(task_choice.get("confidence", 0.5))

        noul_choice = answers.get("can_handle_locally", {})
        local_noul = float(noul_choice.get("noul", 0.5))

        # Calculate base matching rate
        matching_rate = round(type_conf * local_noul, 4)

        # Process Star Skill Match
        matched_skill = None
        skill_domain = None
        preflight_passed = True
        preflight_details = "N/A"
        guarantee_badge = "Standard"

        if selected_type_str.startswith("skill:"):
            skill_id = selected_type_str.replace("skill:", "")
            matched_skill = skill_id
            task_type = TaskType.STAR_SKILL

            # Check if this is a known top star profile with preflight
            profile = TOP_STAR_SKILL_PROFILES.get(skill_id)
            if profile:
                skill_domain = profile.domain
                preflight_passed, preflight_details = profile.precondition_check()
                if preflight_passed:
                    guarantee_badge = "Verified & Ready"
                    recommended_tier = RoutingTier.TIER_2_JEV_DECISION
                    rationale = f"Top Star 스킬 [{profile.display_name}]과 {matching_rate:.1%} 매칭. 사전환경 통과: {preflight_details}."
                else:
                    guarantee_badge = "Pre-flight Warning"
                    recommended_tier = RoutingTier.TIER_3_FOUNDATION_LLM
                    rationale = f"스킬 [{profile.display_name}] 추천이나 사전조건 불만족({preflight_details}). 상위 LLM으로 우회합니다."
            else:
                skill_domain = "Custom Installed"
                guarantee_badge = "Discovered Skill"
                recommended_tier = RoutingTier.TIER_2_JEV_DECISION
                rationale = f"설치된 에이전트 스킬 [{skill_id}]과 매칭({matching_rate:.1%})되었습니다."

        else:
            try:
                task_type = TaskType(selected_type_str)
            except ValueError:
                task_type = TaskType.UNKNOWN

            rule_threshold = self.settings.rule_threshold
            jev_threshold = self.settings.jev_threshold

            if matching_rate >= rule_threshold and task_type == TaskType.DETERMINISTIC_RULE:
                recommended_tier = RoutingTier.TIER_1_LOCAL_RULE
                guarantee_badge = "Zero Token Rule"
                rationale = f"높은 일치율({matching_rate:.1%})로 로컬 규칙 엔진(임계값 {rule_threshold:.0%})에서 즉시 처리 가능합니다."
            elif matching_rate >= jev_threshold and task_type == TaskType.JEV_STRUCTURED:
                recommended_tier = RoutingTier.TIER_2_JEV_DECISION
                guarantee_badge = "Jev Bound"
                rationale = f"구조적 판별 작업으로 Jev System One({matching_rate:.1%})에서 초고속 처리가 권장됩니다."
            else:
                recommended_tier = RoutingTier.TIER_3_FOUNDATION_LLM
                guarantee_badge = "Escalated to LLM"
                rationale = f"작업 복잡도 또는 낮은 로컬 적합도({matching_rate:.1%})로 인해 파운데이션 LLM으로 에스컬레이션합니다."

        return ClassificationResult(
            prompt=prompt,
            task_type=task_type,
            type_confidence=type_conf,
            can_handle_locally=local_noul,
            matching_rate=matching_rate,
            recommended_tier=recommended_tier,
            rationale=rationale,
            matched_skill=matched_skill,
            skill_domain=skill_domain,
            preflight_passed=preflight_passed,
            preflight_details=preflight_details,
            guarantee_badge=guarantee_badge,
            raw_response=data
        )

    def _heuristic_fallback(self, prompt: str, rationale: str) -> ClassificationResult:
        """Fast offline heuristic mapping against Top Star Skills."""
        lower = prompt.lower()
        
        # Check Star Skill Triggers
        for sid, prof in TOP_STAR_SKILL_PROFILES.items():
            if any(trig.lower() in lower for trig in prof.positive_triggers):
                passed, details = prof.precondition_check()
                badge = "Verified & Ready" if passed else "Pre-flight Warning"
                return ClassificationResult(
                    prompt=prompt,
                    task_type=TaskType.STAR_SKILL,
                    type_confidence=0.92,
                    can_handle_locally=0.90 if passed else 0.40,
                    matching_rate=0.828 if passed else 0.368,
                    recommended_tier=RoutingTier.TIER_2_JEV_DECISION if passed else RoutingTier.TIER_3_FOUNDATION_LLM,
                    rationale=f"오프라인 룰: Top Star 스킬 [{prof.display_name}] 감지. 사전환경: {details}.",
                    matched_skill=sid,
                    skill_domain=prof.domain,
                    preflight_passed=passed,
                    preflight_details=details,
                    guarantee_badge=badge
                )

        if any(w in lower for w in ["계산", "변환", "정규식", "더하기", "빼기", "format"]):
            task_type = TaskType.DETERMINISTIC_RULE
            matching_rate = 0.85
            tier = RoutingTier.TIER_1_LOCAL_RULE
            badge = "Zero Token Rule"
        elif any(w in lower for w in ["매칭", "연결", "분류", "정답지", "쪽수"]):
            task_type = TaskType.JEV_STRUCTURED
            matching_rate = 0.75
            tier = RoutingTier.TIER_2_JEV_DECISION
            badge = "Jev Bound"
        elif any(w in lower for w in ["그림", "사진", "그래프", "도형", "ocr", "이미지"]):
            task_type = TaskType.VISION_OCR
            matching_rate = 0.20
            tier = RoutingTier.TIER_3_FOUNDATION_LLM
            badge = "Vision Required"
        else:
            task_type = TaskType.COMPLEX_REASONING
            matching_rate = 0.15
            tier = RoutingTier.TIER_3_FOUNDATION_LLM
            badge = "Escalated to LLM"

        return ClassificationResult(
            prompt=prompt,
            task_type=task_type,
            type_confidence=0.8,
            can_handle_locally=matching_rate,
            matching_rate=matching_rate,
            recommended_tier=tier,
            rationale=rationale,
            guarantee_badge=badge
        )
