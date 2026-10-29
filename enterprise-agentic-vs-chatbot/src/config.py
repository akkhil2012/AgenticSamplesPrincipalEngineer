import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./workflows.db")
    model: str = os.getenv("MODEL_NAME", "mock")
    model_timeout: float = float(os.getenv("MODEL_TIMEOUT_SECONDS", "15"))
    model_retries: int = int(os.getenv("MODEL_RETRIES", "2"))
    approval_ttl: int = int(os.getenv("APPROVAL_TTL_SECONDS", "900"))
    rate_limit: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    demo_auth: bool = os.getenv("DEMO_AUTH", "true").lower() == "true"
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
