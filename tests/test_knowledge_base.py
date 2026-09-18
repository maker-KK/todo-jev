"""Tests for SkillKnowledgeBase and canonical skill linking."""
import pytest
from app.knowledge_base import SkillKnowledgeBase
from app.skill_registry import SkillRegistry

def test_knowledge_base_loading():
    kb = SkillKnowledgeBase()
    profiles = kb.list_profiles()
    assert len(profiles) == 20
    
    spec_driven = kb.get_profile("tlc-spec-driven")
    assert spec_driven is not None
    assert spec_driven.domain == "Planning & Architecture"
    assert len(spec_driven.application_conditions) > 0
    assert len(spec_driven.exclusion_conditions) > 0

def test_canonical_identity_verification():
    kb = SkillKnowledgeBase()
    registry = SkillRegistry()
    installed = registry.discover_skills()
    
    assert "tlc-spec-driven" in installed
    path = installed["tlc-spec-driven"].path
    matched, msg = kb.verify_canonical_identity("tlc-spec-driven", path)
    assert matched is True
    assert "Verified canonical match" in msg

def test_criteria_generation():
    kb = SkillKnowledgeBase()
    baseline = kb.build_baseline_criteria()
    assert len(baseline) == 20
    assert "skill:tlc-spec-driven" in baseline

    profile_criteria = kb.build_profile_criteria()
    assert len(profile_criteria) == 20
    assert "제외:" in profile_criteria["skill:tlc-spec-driven"]
