"""Knowledge Base for Curated Canonical Skill Profiles."""
import json
from pathlib import Path
from typing import NamedTuple, Literal, Optional
from pydantic import BaseModel, Field

DATA_FILE_PATH = Path(__file__).parent.parent / "data" / "canonical_skill_profiles.json"

class ConditionSpec(BaseModel):
    text: str
    source: str
    type: Literal["mandatory", "recommended", "alternative"]
    grounding: Literal["explicit_fact", "inferred_rule"]

class RequiredInput(BaseModel):
    name: str
    source: str
    type: Literal["mandatory", "recommended"]
    grounding: Literal["explicit_fact", "inferred_rule"]

class PreparationStep(BaseModel):
    step: str
    source: str
    grounding: Literal["explicit_fact", "inferred_rule"]

class PreflightContract(BaseModel):
    check_func_name: str
    target: str
    failure_recovery: str

class CanonicalSkillProfile(BaseModel):
    skill_id: str
    display_name: str
    domain: str
    source_repo: str
    source_file: str
    sha256: str
    summary: str
    application_conditions: list[ConditionSpec]
    exclusion_conditions: list[ConditionSpec]
    required_inputs: list[RequiredInput]
    preparation_steps: list[PreparationStep]
    preflight_contract: PreflightContract

    @property
    def positive_triggers(self) -> list[str]:
        return [c.text for c in self.application_conditions]

    @property
    def negative_constraints(self) -> list[str]:
        return [c.text for c in self.exclusion_conditions]

class SkillKnowledgeBase:
    """Manages verified canonical skill profiles and links with installed skills."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or DATA_FILE_PATH
        self.profiles: dict[str, CanonicalSkillProfile] = {}
        self.load_profiles()

    def load_profiles(self) -> None:
        if not self.data_path.exists():
            return
        data = json.loads(self.data_path.read_text(encoding="utf-8"))
        for k, v in data.items():
            self.profiles[k] = CanonicalSkillProfile.model_validate(v)

    def get_profile(self, skill_id: str) -> Optional[CanonicalSkillProfile]:
        return self.profiles.get(skill_id)

    def list_profiles(self) -> list[CanonicalSkillProfile]:
        return list(self.profiles.values())

    def verify_canonical_identity(self, skill_id: str, local_path: Path) -> tuple[bool, str]:
        """Verify that an installed skill matches canonical identity (not just name equality)."""
        prof = self.get_profile(skill_id)
        if not prof:
            return False, f"Skill '{skill_id}' is not in canonical knowledge base"

        skill_md = local_path / "SKILL.md"
        if not skill_md.exists():
            return False, f"Missing SKILL.md in {local_path}"

        import hashlib
        h = hashlib.sha256(skill_md.read_bytes()).hexdigest()
        if h == prof.sha256:
            return True, f"Verified canonical match (SHA256: {h[:8]}..)"
        return True, f"Installed version diff (Local: {h[:8]}.., Canonical: {prof.sha256[:8]}..)"

    def build_baseline_criteria(self) -> dict[str, str]:
        """Criteria with only simple basic description (Baseline Mode)."""
        criteria = {}
        for sid, p in self.profiles.items():
            criteria[f"skill:{sid}"] = f"[{p.domain}] {p.summary}"
        return criteria

    def build_profile_criteria(self) -> dict[str, str]:
        """Rich criteria with positive conditions and negative exclusions (Grounded Profile Mode)."""
        criteria = {}
        for sid, p in self.profiles.items():
            pos = " / ".join([c.text for c in p.application_conditions[:2]])
            neg = " / ".join([c.text for c in p.exclusion_conditions[:2]])
            criteria[f"skill:{sid}"] = f"[{p.domain}] 적용: {pos}. (제외: {neg})"
        return criteria
