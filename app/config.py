"""Configuration settings for To do - Jev."""
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    """Global configuration settings."""
    # Thresholds
    rule_threshold: float = Field(default=float(os.getenv("JEV_RULE_THRESHOLD", "0.70")), ge=0.0, le=1.0)
    jev_threshold: float = Field(default=float(os.getenv("JEV_THRESHOLD", "0.50")), ge=0.0, le=1.0)
    
    # Report Format: 'one_line' (default), 'detailed', 'quiet'
    report_format: str = Field(default=os.getenv("JEV_REPORT_FORMAT", "one_line"))
    
    # Skill Auto-Sync Toggle
    auto_sync_skills: bool = Field(default=os.getenv("JEV_AUTO_SYNC_SKILLS", "true").lower() in ("true", "1", "yes"))
    
    # Skill Directories
    local_skills_dir: str = os.getenv("JEV_LOCAL_SKILLS_DIR", ".agent/skills")
    global_skills_dir: str = os.getenv("JEV_GLOBAL_SKILLS_DIR", os.path.expanduser("~/.gemini/antigravity/skills"))

# Default shared settings instance
settings = Settings()
