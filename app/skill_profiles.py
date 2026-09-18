"""Curated Top Star Skill Profiles from GitHub AI Agent Ecosystem."""
from typing import Callable, NamedTuple
from app.preflight import PreflightChecker
from app.models import TaskType

class StarSkillProfile(NamedTuple):
    skill_id: str
    display_name: str
    domain: str
    summary: str
    positive_triggers: list[str]
    negative_constraints: list[str]
    precondition_check: Callable[[], tuple[bool, str]]
    recommended_action: str

    @property
    def name(self) -> str:
        return self.skill_id

TOP_STAR_SKILL_PROFILES: dict[str, StarSkillProfile] = {
    "tlc-spec-driven": StarSkillProfile(
        skill_id="tlc-spec-driven",
        display_name="Spec-Driven Feature Planner (EARS)",
        domain="Planning & Architecture",
        summary="기능 구현 전 EARS 표기법 요구사항 명세, 원자적 태스크 분할, 결정론적 검증 게이트 수립.",
        positive_triggers=["기능 기획", "스펙 작성", "요구사항 명세", "태스크 분할", "EARS", "spec-driven", "구현 계획"],
        negative_constraints=["단순 1줄 버그 수정", "오탈자 수정", "패키지 단순 업데이트"],
        precondition_check=PreflightChecker.has_git_repo,
        recommended_action="SPECIFY 단계부터 EARS 요구사항 문서 및 원자적 커밋 계획 수립"
    ),
    "tactical-ddd": StarSkillProfile(
        skill_id="tactical-ddd",
        display_name="Tactical Domain-Driven Design",
        domain="Architecture & Refactoring",
        summary="모듈 간 결합도 분석, Bounded Context 분리, 레거시 모놀리스의 점진적 분해.",
        positive_triggers=["도메인 모델링", "모듈 분리", "DDD", "바운디드 컨텍스트", "결합도 분석", "리팩토링"],
        negative_constraints=["단순 UI 스타일 변경", "단순 CRUD 생성"],
        precondition_check=PreflightChecker.has_git_repo,
        recommended_action="도메인 경계 분석 및 의존성 방향(Dependency Inversion) 다이어그램 도출"
    ),
    "playwright-skill": StarSkillProfile(
        skill_id="playwright-skill",
        display_name="Playwright Browser Automator",
        domain="Testing & Web Automation",
        summary="헤드리스 브라우저 테스트, 폼 자동 입력, UI 회귀 스냅샷, 웹 데이터 수집.",
        positive_triggers=["브라우저 자동화", "E2E 테스트", "Playwright", "웹 스크래핑", "화면 캡처", "폼 입력"],
        negative_constraints=["백엔드 순수 알고리즘", "SQL 쿼리 작성"],
        precondition_check=PreflightChecker.has_node_env,
        recommended_action="Playwright 테스트 스크립트 작성 및 헤드리스 브라우저 검증 실행"
    ),
    "security-best-practices": StarSkillProfile(
        skill_id="security-best-practices",
        display_name="Security Best Practices & OWASP Auditor",
        domain="Security & Compliance",
        summary="OWASP Top 10 점검, 하드코딩된 API 시크릿 탐지, SQLi/XSS 취약점 검증.",
        positive_triggers=["보안 점검", "취약점 분석", "시크릿 검사", "OWASP", "인젝션 방지", "보안 감사"],
        negative_constraints=["단순 텍스트 번역", "UI 레이아웃 조정"],
        precondition_check=PreflightChecker.has_dependency_manifest,
        recommended_action="보안 정적 분석(SAST) 리포트 생성 및 취약점 패치 가이드 적용"
    ),
    "figma-implement-design": StarSkillProfile(
        skill_id="figma-implement-design",
        display_name="Figma Design-to-Code Converter",
        domain="Frontend & Design",
        summary="Figma 디자인 토큰 및 레이아웃을 픽셀 퍼펙트 React/Tailwind 코드로 변환.",
        positive_triggers=["피그마 변환", "figma", "디자인 구현", "컴포넌트 개발", "Tailwind UI"],
        negative_constraints=["DB 마이그레이션", "백엔드 API 라우트 설계"],
        precondition_check=PreflightChecker.has_frontend_code,
        recommended_action="디자인 토큰 추출 및 재사용 가능한 UI 컴포넌트 코드 생성"
    ),
    "the-judge": StarSkillProfile(
        skill_id="the-judge",
        display_name="The Judge: Adversarial Code Reviewer",
        domain="Quality & Verification",
        summary="작성자와 검증자를 철저히 분리(Author != Verifier)하여 다중 시각 교차 채점.",
        positive_triggers=["코드 리뷰", "교차 검토", "품질 검증", "PR 리뷰", "독립 채점", "무결성 검사"],
        negative_constraints=["단순 아이디어 브레인스토밍"],
        precondition_check=PreflightChecker.has_python_test_runner,
        recommended_action="독립 검증자 관점에서 엣지 케이스 및 테스트 통과 여부 엄격 판정"
    ),
    "gh-fix-ci": StarSkillProfile(
        skill_id="gh-fix-ci",
        display_name="GitHub Actions & CI Root-Cause Fixer",
        domain="DevOps & Tooling",
        summary="CI/CD 파이프라인 실패 로그의 근본 원인(RCA) 분석 및 자동 복구 패치.",
        positive_triggers=["CI 실패", "GitHub Actions 오류", "빌드 깨짐", "파이프라인 복구", "CI 디버깅"],
        negative_constraints=["신규 비즈니스 기능 기획"],
        precondition_check=PreflightChecker.has_git_repo,
        recommended_action="실패 로그 파싱 후 재현 가능한 로컬 테스트 스크립트 작성 및 패치"
    )
}

def get_curated_skill_profiles() -> list[StarSkillProfile]:
    """Retrieve all curated top star skill profiles."""
    return list(TOP_STAR_SKILL_PROFILES.values())

def find_matching_skill_profiles(target: TaskType | str) -> list[StarSkillProfile]:
    """Find skill profiles matching task type or query keyword."""
    if isinstance(target, TaskType):
        if target in (TaskType.JEV_STRUCTURED, TaskType.STAR_SKILL):
            return [TOP_STAR_SKILL_PROFILES["tlc-spec-driven"], TOP_STAR_SKILL_PROFILES["tactical-ddd"]]
        elif target == TaskType.COMPLEX_REASONING:
            return [TOP_STAR_SKILL_PROFILES["the-judge"]]
        return []

    q = str(target).lower()
    matches = []
    for prof in TOP_STAR_SKILL_PROFILES.values():
        if any(trig.lower() in q for trig in prof.positive_triggers) or prof.domain.lower() in q or prof.skill_id in q:
            matches.append(prof)
    return matches
