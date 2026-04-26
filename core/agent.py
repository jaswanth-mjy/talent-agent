from typing import Callable, Dict, List, Optional

from core.config import DATA_PATH, DEFAULT_SETTINGS
from memory.conversation_store import ConversationStore
from modules.engagement import simulate_conversation
from modules.interest import calculate_interest_score
from modules.jd_parser import parse_jd
from modules.matcher import calculate_match_score
from modules.ranking import rank_candidates
from modules.search import CandidateSearch


class TalentAgent:
	def __init__(self, data_path: str = str(DATA_PATH)):
		self.settings = DEFAULT_SETTINGS
		self.search_engine = CandidateSearch(
			data_path=data_path,
			embedding_model=self.settings.embedding_model,
			strict_embeddings=self.settings.strict_ollama,
		)
		self.conversation_store = ConversationStore()

	def _notify_progress(
		self,
		progress_callback: Optional[Callable[[str, str], None]],
		stage: str,
		message: str,
	) -> None:
		if progress_callback:
			progress_callback(stage, message)

	def run(
		self,
		jd_text: str,
		top_k: int = None,
		progress_callback: Optional[Callable[[str, str], None]] = None,
	) -> Dict:
		if not jd_text or not jd_text.strip():
			raise ValueError("JD text cannot be empty.")

		self._notify_progress(progress_callback, "JD Parsing", "Parsing job description...")
		parsed_jd = parse_jd(jd_text)
		self._notify_progress(
			progress_callback,
			"JD Parsing",
			f"Parsed role: {parsed_jd.get('role', 'Unknown')} | Skills: {', '.join(parsed_jd.get('skills', [])[:5]) or 'None'}",
		)
		effective_top_k = top_k or self.settings.top_k

		self._notify_progress(progress_callback, "Discovery", "Searching candidate profiles...")
		candidates = self.search_engine.search(parsed_jd, top_k=effective_top_k)
		self._notify_progress(
			progress_callback,
			"Discovery",
			f"Found {len(candidates)} candidate(s) for ranking.",
		)
		scored_candidates: List[Dict] = []

		for index, candidate in enumerate(candidates, start=1):
			candidate_name = candidate.get("name", "Unknown")
			self._notify_progress(
				progress_callback,
				"Matching",
				f"Scoring match for {candidate_name} ({index}/{len(candidates)})...",
			)
			match_data = calculate_match_score(parsed_jd, candidate)
			self._notify_progress(
				progress_callback,
				"Outreach",
				f"Simulating outreach conversation for {candidate_name}...",
			)
			conversation = simulate_conversation(
				parsed_jd,
				candidate,
				turns=self.settings.max_turns,
				use_llm=self.settings.use_llm_conversation,
			)
			interest_score = calculate_interest_score(conversation)
			self._notify_progress(
				progress_callback,
				"Scoring",
				f"Computed interest score for {candidate_name}: {interest_score}",
			)

			self.conversation_store.save(candidate_name, conversation)

			scored_candidates.append(
				{
					"name": candidate_name,
					"match_score": match_data["match_score"],
					"skill_score": match_data["skill_score"],
					"experience_score": match_data["experience_score"],
					"required_experience": parsed_jd.get("experience_years", 0),
					"candidate_experience": candidate.get("experience", 0),
					"matched_skills": match_data["matched_skills"],
					"missing_skills": match_data["missing_skills"],
					"interest_score": interest_score,
					"conversation": conversation,
					"similarity_score": candidate.get("similarity_score", 0),
				}
			)

		self._notify_progress(progress_callback, "Ranking", "Ranking candidates and generating explanations...")
		ranked = rank_candidates(scored_candidates)
		self._notify_progress(
			progress_callback,
			"Complete",
			f"Completed shortlist with {len(ranked)} ranked candidate(s).",
		)

		return {
			"parsed_jd": parsed_jd,
			"results": ranked,
		}
