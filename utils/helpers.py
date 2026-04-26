import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
	file_path = Path(path)
	with file_path.open("r", encoding="utf-8") as file:
		return json.load(file)


def dump_json(path: str, data: Any) -> None:
	file_path = Path(path)
	with file_path.open("w", encoding="utf-8") as file:
		json.dump(data, file, indent=2)


def print_ranked_results(results):
	for idx, candidate in enumerate(results, start=1):
		print(
			f"{idx}. {candidate['name']} | "
			f"match={candidate['match_score']} | "
			f"interest={candidate['interest_score']} | "
			f"final={candidate['final_score']}"
		)
