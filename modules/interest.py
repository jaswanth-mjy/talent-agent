from typing import Dict, List


POSITIVE_KEYWORDS = {
	"interested",
	"excited",
	"great",
	"yes",
	"love",
	"happy",
	"continue",
	"open",
	"sounds good",
}
NEGATIVE_KEYWORDS = {
	"not interested",
	"decline",
	"busy",
	"no",
	"not now",
	"maybe later",
	"uncertain",
	"reject",
}


def calculate_interest_score(chat_history: List[Dict]) -> int:
	if not chat_history:
		return 50

	candidate_lines = [
		turn.get("message", "").lower()
		for turn in chat_history
		if turn.get("speaker", "").lower() == "candidate"
	]
	if not candidate_lines:
		return 50

	positive_hits = 0
	negative_hits = 0

	for line in candidate_lines:
		for keyword in POSITIVE_KEYWORDS:
			if keyword in line:
				positive_hits += 1
		for keyword in NEGATIVE_KEYWORDS:
			if keyword in line:
				negative_hits += 1

	base = 55
	score = base + (positive_hits * 12) - (negative_hits * 18)
	return max(0, min(100, score))
