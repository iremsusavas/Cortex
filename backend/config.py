"""Application settings and environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment."""

    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # optional fallback
    TAVILY_API_KEY: str = ""  # optional for dev

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cortex.db"
    REDIS_URL: str = "redis://localhost:6379"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # LLM Settings
    PRIMARY_LLM_PROVIDER: str = "anthropic"  # "anthropic" or "openai"
    DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    MAX_TOKENS_PER_AGENT: int = 4096
    TEMPERATURE: float = 0.3

    # Rate Limits
    MAX_CONCURRENT_RESEARCH: int = 5
    MAX_REQUESTS_PER_MINUTE: int = 30

    # Research Settings
    MAX_SEARCH_RESULTS: int = 10
    MAX_RESEARCH_DEPTH: int = 3  # max iteration loops
    MAX_SUB_TASKS: int = 2  # limit sub-tasks for faster demos (was 5)
    MAX_SOURCES_PER_TASK: int = 2  # sources per sub-task (was 3)
    SKIP_SCRAPING: bool = True  # use search snippets only, much faster
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
