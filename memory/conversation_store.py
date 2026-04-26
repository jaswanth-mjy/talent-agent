from typing import Dict, List


class ConversationStore:
	def __init__(self):
		self._store: Dict[str, List[Dict]] = {}

	def save(self, candidate_name: str, history: List[Dict]) -> None:
		self._store[candidate_name] = history

	def get(self, candidate_name: str) -> List[Dict]:
		return self._store.get(candidate_name, [])

	def all(self) -> Dict[str, List[Dict]]:
		return dict(self._store)
