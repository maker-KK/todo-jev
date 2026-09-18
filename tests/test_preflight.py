"""Tests for Skill Profiles and Preflight Verification."""
import pytest
from app.skill_profiles import get_curated_skill_profiles, find_matching_skill_profiles
from app.preflight import run_preflight_checks
from app.models import TaskType

def test_curated_skill_profiles_exist():
    profiles = get_curated_skill_profiles()
    assert len(profiles) >= 6
    names = [p.name for p in profiles]
    assert "tlc-spec-driven" in names
    assert "tactical-ddd" in names
    assert "playwright-skill" in names
    assert "security-best-practices" in names

def test_matching_skill_profiles():
    matches = find_matching_skill_profiles(TaskType.JEV_STRUCTURED)
    assert len(matches) > 0
    match_names = [m.name for m in matches]
    assert "tlc-spec-driven" in match_names

def test_preflight_runner_executes():
    profiles = get_curated_skill_profiles()
    spec_driven = next(p for p in profiles if p.name == "tlc-spec-driven")
    report = run_preflight_checks(spec_driven)
    assert report.skill_name == "tlc-spec-driven"
    assert isinstance(report.passed, bool)
    assert len(report.checks) > 0
