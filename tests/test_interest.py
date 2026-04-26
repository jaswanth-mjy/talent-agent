import unittest

from modules.interest import calculate_interest_score


class TestInterestScore(unittest.TestCase):
    def test_high_interest(self):
        chat = [
            {"speaker": "candidate", "message": "Yes, I am interested and excited."},
            {"speaker": "candidate", "message": "Sounds good, happy to continue."},
        ]
        score = calculate_interest_score(chat)
        self.assertGreaterEqual(score, 80)

    def test_low_interest(self):
        chat = [
            {"speaker": "candidate", "message": "No, not interested right now."},
            {"speaker": "candidate", "message": "Maybe later, I am busy."},
        ]
        score = calculate_interest_score(chat)
        self.assertLessEqual(score, 30)


if __name__ == "__main__":
    unittest.main()
