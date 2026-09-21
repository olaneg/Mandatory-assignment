import unittest
from data_generator import generate_fitness_data
from sample_data import SCENARIOS
from main import (
    Observation, Participant, Session, SessionAnalyzer,
    validate_observation, summarize, compare_to_reference, detect_recovery,
)

class TestValidation(unittest.TestCase):

    def test_valid_observation_passes(self):
        data = {"timestamp": 1, "heart_rate": 70, "skin_response": 1.0,
                "temperature": 33.0, "activity_level": 0.1, "signal_quality": 0.9}
        self.assertTrue(validate_observation(data)["valid"])

    def test_impossible_heart_rate_flagged(self):
        data = {"timestamp": 1, "heart_rate": 300, "skin_response": 1.0,
                "temperature": 33.0, "activity_level": 0.1, "signal_quality": 0.9}
        self.assertFalse(validate_observation(data)["valid"])


class TestCalculations(unittest.TestCase):

    def test_summarize_basic(self):
        result = summarize([60, 70, 80])
        self.assertEqual(result["average"], 70)

    def test_detect_recovery_true(self):
        hr = [140, 142, 141, 100, 90, 80]
        act = [0.8, 0.8, 0.8, 0.4, 0.3, 0.2]
        self.assertTrue(detect_recovery(hr, act))


class TestScenarios(unittest.TestCase):

    def _analyze(self, name):
        profile, observations = SCENARIOS[name]
        session = Session(Participant.from_profile(profile), observations)
        return SessionAnalyzer(session).analyze()

    def test_resting_classified_as_resting(self):
        self.assertEqual(self._analyze("resting")["classification"], "resting")

    def test_poor_quality_flags_insufficient_data(self):
        self.assertEqual(self._analyze("poor_quality")["classification"], "insufficient data")


if __name__ == "__main__":
    unittest.main()