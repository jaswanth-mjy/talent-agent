from dataclasses import dataclass
import os
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
	ollama_base_url: str = "http://localhost:11434/api"
	llm_model: str = "llama3"
	embedding_model: str = "nomic-embed-text"
	top_k: int = 5
	max_turns: int = 3
	strict_ollama: bool = _env_bool("STRICT_OLLAMA", False)
	use_llm_conversation: bool = _env_bool("USE_LLM_CONVERSATION", False)


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "candidates.json"
DEFAULT_SETTINGS = Settings()
