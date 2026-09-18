"""Skill Registry for discovering and syncing installed agent skills with Jev."""
import re
from pathlib import Path
from typing import NamedTuple

class SkillMetadata(NamedTuple):
    name: str
    description: str
    path: Path

class SkillRegistry:
    """Discovers installed skills and generates Jev classification criteria."""

    def __init__(self, search_paths: list[str | Path] | None = None):
        if search_paths:
            self.search_paths = [Path(p) for p in search_paths]
        else:
            self.search_paths = [
                Path(".agent/skills"),
                Path("../cjbs-backend/.agent/skills"),
                Path(Path.home() / ".gemini/antigravity/skills")
            ]

    def discover_skills(self) -> dict[str, SkillMetadata]:
        """Scan directories for SKILL.md files and parse their metadata."""
        skills: dict[str, SkillMetadata] = {}

        for base_path in self.search_paths:
            if not base_path.exists():
                continue

            for skill_file in base_path.glob("*/SKILL.md"):
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    name, desc = self._parse_frontmatter(content, default_name=skill_file.parent.name)
                    if name and name not in skills:
                        skills[name] = SkillMetadata(name=name, description=desc, path=skill_file.parent)
                except Exception:
                    continue

        return skills

    def build_jev_criteria(self, max_skills: int = 50) -> dict[str, str]:
        """Convert discovered skills into Jev Choice criteria."""
        skills = self.discover_skills()
        if not skills:
            return {}

        criteria: dict[str, str] = {}
        # Prioritize and trim descriptions for prompt efficiency
        for name, meta in list(skills.items())[:max_skills]:
            # Compact description to ~120 chars
            clean_desc = meta.description.strip().replace("\n", " ")
            if len(clean_desc) > 120:
                clean_desc = clean_desc[:117] + "..."
            criteria[name] = clean_desc

        return criteria

    def _parse_frontmatter(self, content: str, default_name: str) -> tuple[str, str]:
        """Extract name and description from YAML frontmatter."""
        name = default_name
        description = "Specialized agent skill workflow."

        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            name_match = re.search(r"^name:\s*([^\n]+)", frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()

            desc_match = re.search(r"^description:\s*(?:>-\s*|\s*)([^\n]+(?:\n\s+[^\n]+)*)", frontmatter, re.MULTILINE)
            if desc_match:
                raw_desc = desc_match.group(1)
                # Unfold YAML multiline string
                description = " ".join(line.strip() for line in raw_desc.splitlines())

        return name, description
