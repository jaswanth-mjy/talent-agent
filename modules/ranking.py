from typing import Dict, List


def _recommendation(final_score: float, match_score: float, interest_score: float) -> str:
	if final_score >= 80 and match_score >= 75 and interest_score >= 60:
		return "Fast-track to interview"
	if final_score >= 65 and match_score >= 60:
		return "Proceed to recruiter screen"
	if final_score >= 50:
		return "Keep in warm shortlist"
	return "Low priority"


def rank_candidates(candidate_results: List[Dict]) -> List[Dict]:
	ranked = []
	for item in candidate_results:
		match_score = float(item.get("match_score", 0))
		interest_score = float(item.get("interest_score", 0))
		final_score = (0.6 * match_score) + (0.4 * interest_score)
		skill_score = float(item.get("skill_score", 0))
		experience_score = float(item.get("experience_score", 0))
		similarity_score = float(item.get("similarity_score", 0))

		explanation = []
		matched_skills = item.get("matched_skills", [])
		missing_skills = item.get("missing_skills", [])
		recommendation = _recommendation(final_score, match_score, interest_score)
		total_skills = len(matched_skills) + len(missing_skills)
		skill_coverage = round((len(matched_skills) / total_skills) * 100, 2) if total_skills else 0.0
		experience_gap = max(0.0, float(item.get("required_experience", 0)) - float(item.get("candidate_experience", 0)))

		if matched_skills:
			explanation.append("Matches " + ", ".join(matched_skills[:3]))
		if missing_skills:
			explanation.append("Missing " + ", ".join(missing_skills[:3]))

		if interest_score >= 75:
			explanation.append("Highly interested")
		elif interest_score >= 45:
			explanation.append("Moderately interested")
		else:
			explanation.append("Low interest")

		explanation.append(recommendation)

		ranked.append(
			{
				"name": item.get("name", "Unknown"),
				"match_score": round(match_score, 2),
				"interest_score": round(interest_score, 2),
				"final_score": round(final_score, 2),
				"skill_score": round(skill_score, 2),
				"experience_score": round(experience_score, 2),
				"similarity_score": round(similarity_score, 4),
				"skill_coverage": round(skill_coverage, 2),
				"experience_gap": round(experience_gap, 2),
				"recommendation": recommendation,
				"explanation": explanation,
				"conversation": item.get("conversation", []),
			}
		)

	return sorted(ranked, key=lambda x: x["final_score"], reverse=True)
