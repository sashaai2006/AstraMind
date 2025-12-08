from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

try:
    # Pydantic v2 (pydantic-settings)
    from pydantic_settings import BaseSettings
    from pydantic import Field
    PYDANTIC_V2 = True
except ImportError:
    # Pydantic v1 fallback
    from pydantic import BaseSettings, Field
    PYDANTIC_V2 = False


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    projects_root: Path = Field(default=Path("./projects"))
    llm_mode: Literal["mock", "ollama", "groq", "github", "deepseek", "cerebras"] = Field(
        default="deepseek"
    )
    
    # Model configurations
    ollama_model: str = Field(default="llama3.2:3b")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    github_model: str = Field(default="gpt-4o")  # gpt-4o, claude-3-5-sonnet, llama-3.1-70b
    deepseek_model: str = Field(default="deepseek-chat")  # deepseek-chat or deepseek-coder
    cerebras_model: str = Field(default="llama3.1-70b")  # llama3.1-8b or llama3.1-70b
    
    llm_semaphore: int = Field(default=10)  # Increased for parallelism
    github_api_url: str = Field(default="https://api.github.com")
    admin_api_key: Optional[str] = Field(default=None)

    if PYDANTIC_V2:
        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore"
        }
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.projects_root.mkdir(parents=True, exist_ok=True)
    return settings
