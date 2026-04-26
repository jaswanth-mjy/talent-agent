import json
import re
from typing import Dict, List

from llm.ollama_client import generate


def _extract_json_array(text: str):
	match = re.search(r"\[.*\]", text, re.DOTALL)
	if not match:
		return None
	try:
		parsed = json.loads(match.group())
		if isinstance(parsed, list):
			return parsed
	except json.JSONDecodeError:
		return None
	return None


def _fallback_conversation(jd_data: Dict, candidate: Dict) -> List[Dict]:
	return [
		{
			"speaker": "recruiter",
			"message": f"Hi {candidate.get('name', 'there')}, are you open to a {jd_data.get('role', 'role')} opportunity?",
		},
		{
			"speaker": "candidate",
			"message": "Yes, I am interested and would like to know the team expectations.",
		},
		{
			"speaker": "recruiter",
			"message": "Great. This role needs strong skills in "
			+ ", ".join(jd_data.get("skills", [])[:3])
			+ ".",
		},
		{
			"speaker": "candidate",
			"message": "That aligns with my background. I would like to continue this process.",
		},
	]


def simulate_conversation(
	jd_data: Dict,
	candidate: Dict,
	turns: int = 3,
	use_llm: bool = False,
) -> List[Dict]:
	if not use_llm:
		return _fallback_conversation(jd_data, candidate)

	safe_turns = max(2, min(turns, 3))
	prompt = f"""
You are simulating a recruiter and a candidate chat.

Return ONLY a JSON array of messages.
Each message format:
{{"speaker": "recruiter"|"candidate", "message": "..."}}

Rules:
1) Exactly {safe_turns * 2} messages
2) Alternate recruiter then candidate
3) Keep each message under 30 words
4) Candidate tone should reflect realistic interest level

Job data:
{json.dumps(jd_data)}

Candidate data:
{json.dumps(candidate)}
"""

	response = generate(prompt)
	history = _extract_json_array(response)

	if history:
		return history

	return _fallback_conversation(jd_data, candidate)
