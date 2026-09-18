import statistics
from sample_data import SCENARIOS

def format_report(result):
    lines = []
    lines.append(f"Participant: {result['participant_id']}")
    lines.append(f"Usable observations: {result['usable_observations']} / {result['total_observations']}")
    lines.append(f"Classification: {result['classification']}")
    lines.append(f"Explanation: {result['explanation']}")
    return "\n".join(lines)

def validate_observation(data):
    """
    Validate a single raw observation dictionary against the ranges given
    in DATA_DESCRIPTION.md.
    """
    required_fields = [
        "timestamp", "heart_rate", "skin_response",
        "temperature", "activity_level", "signal_quality",
    ]
    reasons = []

    for field in required_fields:
        if field not in data or data[field] is None:
            reasons.append(f"missing field: {field}")

    if reasons:
        return {"valid": False, "reasons": reasons}

    if not (35 <= data["heart_rate"] <= 205):
        reasons.append("heart_rate outside normal range (35-205 bpm)")

    if data["skin_response"] < 0:
        reasons.append("skin_response can't be negative")

    if not (25 <= data["temperature"] <= 42):
        reasons.append("temperature outside normal range (25-42 C)")

    if not (0 <= data["activity_level"] <= 1):
        reasons.append("activity_level outside normal range (0-1)")

    if not (0 <= data["signal_quality"] <= 1):
        reasons.append("signal_quality outside reliability indicator (0-1) ")
    
    return {"valid": len(reasons) == 0, "reasons": reasons}

def summarize(values):
    if not values:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0}
    return {
        "average": round(statistics.mean(values), 2),
        "minimum": round(min(values), 2),
        "maximum": round(max(values), 2),
    }


def compare_to_reference(value, reference, tolerance=0.15):
    if reference == 0:
        return "within"
    diff_ratio = (value - reference) / reference
    if diff_ratio > tolerance:
        return "above"
    if diff_ratio < -tolerance:
        return "below"
    return "within"

def detect_recovery(heart_rates, activity_levels):
    n = len(heart_rates)
    if n < 6:
        return False

    third = n // 3
    mid_hr = statistics.mean(heart_rates[third:2 * third])
    end_hr = statistics.mean(heart_rates[2 * third:])
    mid_act = statistics.mean(activity_levels[third:2 * third])
    end_act = statistics.mean(activity_levels[2 * third:])

    return end_hr < mid_hr * 0.9 and end_act < mid_act * 0.9

class Observation:
    def __init__(self, timestamp, heart_rate, skin_response,
                 temperature, activity_level, signal_quality):
        self.timestamp = timestamp
        self.heart_rate = heart_rate
        self.skin_response = skin_response
        self.temperature = temperature
        self.activity_level = activity_level
        self.signal_quality = signal_quality

        validation = validate_observation(self.as_dict())
        self._valid = validation["valid"]
        self._reasons = validation["reasons"]

    def as_dict(self):
        return {
            "timestamp": self.timestamp,
            "heart_rate": self.heart_rate,
            "skin_response": self.skin_response,
            "temperature": self.temperature,
            "activity_level": self.activity_level,
            "signal_quality": self.signal_quality,
        }

    @property
    def is_valid(self):
        return self._valid

    @property
    def reasons(self):
        return list(self._reasons)

class Participant:
    def __init__(self, participant_id, baseline_heart_rate,
                 baseline_skin_response, baseline_temperature):
        self.participant_id = participant_id
        self._baseline = {
            "baseline_heart_rate": baseline_heart_rate,
            "baseline_skin_response": baseline_skin_response,
            "baseline_temperature": baseline_temperature,
        }

    @property
    def baseline(self):
        return dict(self._baseline)

    @classmethod
    def from_profile(cls, profile):
        return cls(
            participant_id=profile["participant_id"],
            baseline_heart_rate=profile["baseline_heart_rate"],
            baseline_skin_response=profile["baseline_skin_response"],
            baseline_temperature=profile["baseline_temperature"],
        )   

class Session:
    def __init__(self, participant, raw_observations):
        self.participant = participant
        self.observations = [
            Observation(
                timestamp=obs["timestamp"],
                heart_rate=obs["heart_rate"],
                skin_response=obs["skin_response"],
                temperature=obs["temperature"],
                activity_level=obs["activity_level"],
                signal_quality=obs["signal_quality"],
            )
            for obs in raw_observations
        ]

    @property
    def valid_observations(self):
        return [obs for obs in self.observations if obs.is_valid]

class SessionAnalyzer:
    MIN_USABLE_OBSERVATIONS = 3
    RESTING_ACTIVITY_THRESHOLD = 0.25
    HIGH_ACTIVITY_THRESHOLD = 0.70

    def __init__(self, session):
        self.session = session

    def analyze(self):
        valid_obs = self.session.valid_observations
        total = len(self.session.observations)
        usable = len(valid_obs)

        if usable < self.MIN_USABLE_OBSERVATIONS:
            return {
                "participant_id": self.session.participant.participant_id,
                "total_observations": total,
                "usable_observations": usable,
                "classification": "insufficient data",
                "explanation": f"Only {usable} usable observation(s); need at least {self.MIN_USABLE_OBSERVATIONS}.",
            }

        heart_rates = [o.heart_rate for o in valid_obs]
        activity_levels = [o.activity_level for o in valid_obs]

        hr_summary = summarize(heart_rates)
        activity_summary = summarize(activity_levels)

        baseline = self.session.participant.baseline
        hr_vs_baseline = compare_to_reference(hr_summary["average"], baseline["baseline_heart_rate"])

        recovery = detect_recovery(heart_rates, activity_levels)

        if recovery:
            classification = "recovering"
            explanation = "Heart rate and activity level both declined near the end of the session."
        elif activity_summary["average"] < self.RESTING_ACTIVITY_THRESHOLD and hr_vs_baseline in ("within", "below"):
            classification = "resting"
            explanation = "Low activity level and heart rate close to or below baseline."
        elif activity_summary["average"] < self.HIGH_ACTIVITY_THRESHOLD:
            classification = "moderate activity"
            explanation = "Moderate activity level and elevated but controlled heart rate."
        else:
            classification = "high activity"
            explanation = "High activity level and heart rate well above baseline."

        return {
            "participant_id": self.session.participant.participant_id,
            "total_observations": total,
            "usable_observations": usable,
            "heart_rate_summary": hr_summary,
            "activity_summary": activity_summary,
            "heart_rate_vs_baseline": hr_vs_baseline,
            "recovery_detected": recovery,
            "classification": classification,
            "explanation": explanation,
        }

def run_all_scenarios():
    for scenario_name, (profile, observations) in SCENARIOS.items():
        participant = Participant.from_profile(profile)
        session = Session(participant, observations)
        result = SessionAnalyzer(session).analyze()

        print(f"\nSCENARIO: {scenario_name}")
        print(format_report(result))


if __name__ == "__main__":
    run_all_scenarios()

    