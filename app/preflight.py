"""Preflight Checker to ground skill guarantees in real environment capabilities."""
import os
import shutil
from pathlib import Path
from typing import NamedTuple, Any

class PreflightReport(NamedTuple):
    skill_name: str
    passed: bool
    details: str
    checks: list[str]

class PreflightChecker:
    """Validates real machine environment preconditions for skills."""

    @staticmethod
    def has_git_repo(path: Path | None = None) -> tuple[bool, str]:
        target = path or Path.cwd()
        current = target.resolve()
        for p in [current, *current.parents]:
            if (p / ".git").exists():
                return True, "Git repository detected (.git folder found)"
        return False, "Not inside a Git repository"

    @staticmethod
    def has_python_test_runner(path: Path | None = None) -> tuple[bool, str]:
        target = path or Path.cwd()
        if (target / "pytest.ini").exists() or (target / "pyproject.toml").exists() or (target / "tests").exists():
            return True, "Python test harness detected (pytest/pyproject/tests)"
        if shutil.which("pytest"):
            return True, "Global pytest binary available in PATH"
        return False, "No Python test runner configuration detected"

    @staticmethod
    def has_node_env(path: Path | None = None) -> tuple[bool, str]:
        target = path or Path.cwd()
        if (target / "package.json").exists() or shutil.which("npm") or shutil.which("node"):
            return True, "Node.js environment detected (package.json or node binary)"
        return False, "Node.js/npm not found in workspace or PATH"

    @staticmethod
    def has_dependency_manifest(path: Path | None = None) -> tuple[bool, str]:
        target = path or Path.cwd()
        manifests = ["requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
        found = [m for m in manifests if (target / m).exists()]
        if found:
            return True, f"Dependency manifest found: {', '.join(found)}"
        return False, "No dependency manifest detected"

    @staticmethod
    def has_frontend_code(path: Path | None = None) -> tuple[bool, str]:
        target = path or Path.cwd()
        ui_dirs = ["src", "components", "pages", "app", "ui"]
        found = [d for d in ui_dirs if (target / d).exists()]
        if found or (target / "tailwind.config.js").exists() or (target / "vite.config.ts").exists():
            return True, "Frontend UI workspace structure detected"
        return False, "No frontend UI directory found"

def run_preflight_checks(profile: Any) -> PreflightReport:
    """Execute preflight check on a skill profile and generate structured report."""
    passed, details = profile.precondition_check()
    skill_name = getattr(profile, "skill_id", getattr(profile, "name", "unknown"))
    return PreflightReport(
        skill_name=skill_name,
        passed=passed,
        details=details,
        checks=[details]
    )
