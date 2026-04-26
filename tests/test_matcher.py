import unittest

from modules.matcher import calculate_match_score


class TestMatcher(unittest.TestCase):
    def test_calculate_match_score_partial_skill_match(self):
        jd = {"skills": ["Python", "Django", "SQL"], "experience_years": 2}
        candidate = {"skills": ["Python", "Flask", "SQL"], "experience": 1}

        result = calculate_match_score(jd, candidate)

        self.assertEqual(result["matched_skills"], ["python", "sql"])
        self.assertEqual(result["missing_skills"], ["django"])
        self.assertAlmostEqual(result["skill_score"], 66.67, places=2)
        self.assertAlmostEqual(result["experience_score"], 50.0, places=2)
        self.assertAlmostEqual(result["match_score"], 61.67, places=2)


if __name__ == "__main__":
    unittest.main()
