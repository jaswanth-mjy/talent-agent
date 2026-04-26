import unittest

from modules.ranking import rank_candidates


class TestRanking(unittest.TestCase):
    def test_rank_candidates_sorted_by_final_score(self):
        candidates = [
            {
                "name": "A",
                "match_score": 90,
                "interest_score": 70,
                "matched_skills": ["python"],
                "missing_skills": ["sql"],
            },
            {
                "name": "B",
                "match_score": 80,
                "interest_score": 90,
                "matched_skills": ["python", "django"],
                "missing_skills": [],
            },
        ]

        ranked = rank_candidates(candidates)

        self.assertEqual(ranked[0]["name"], "B")
        self.assertEqual(ranked[1]["name"], "A")
        self.assertAlmostEqual(ranked[0]["final_score"], 84.0)
        self.assertAlmostEqual(ranked[1]["final_score"], 82.0)


if __name__ == "__main__":
    unittest.main()
