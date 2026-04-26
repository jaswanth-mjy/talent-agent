import hashlib
import re
from typing import Dict, List

import numpy as np

from llm.ollama_client import embed


def normalize_vector(vector: List[float]) -> np.ndarray:
	arr = np.array(vector, dtype="float32")
	if arr.size == 0:
		return arr
	norm = np.linalg.norm(arr)
	if norm == 0:
		return arr
	return arr / norm


def _fallback_embed_text(text: str, dim: int = 256) -> np.ndarray:
	vector = np.zeros(dim, dtype="float32")
	tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
	if not tokens:
		return vector

	for token in tokens:
		digest = hashlib.md5(token.encode("utf-8")).hexdigest()
		index = int(digest, 16) % dim
		vector[index] += 1.0

	return normalize_vector(vector.tolist())


def candidate_to_text(candidate: Dict) -> str:
	skills = ", ".join(candidate.get("skills", []))
	return (
		f"Name: {candidate.get('name', '')}\n"
		f"Role: {candidate.get('role', '')}\n"
		f"Skills: {skills}\n"
		f"Experience: {candidate.get('experience', 0)} years\n"
		f"Profile: {candidate.get('profile', '')}"
	)


def jd_to_text(jd_data: Dict) -> str:
	skills = ", ".join(jd_data.get("skills", []))
	return (
		f"Role: {jd_data.get('role', '')}\n"
		f"Skills: {skills}\n"
		f"Required experience: {jd_data.get('experience_years', 0)} years"
	)


def embed_text(text: str, model: str = "nomic-embed-text", strict: bool = False) -> np.ndarray:
	vector = embed(text, model=model)
	normalized = normalize_vector(vector)
	if normalized.size > 0:
		return normalized
	if strict:
		raise RuntimeError(
			"Embedding generation failed from Ollama. "
			"Ensure Ollama is running and embedding model is available."
		)
	return _fallback_embed_text(text)
