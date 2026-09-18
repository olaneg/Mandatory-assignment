# Smart Fitness Session Analyzer

**Course:** *ACIT 4420 Object-Oriented Python*
**Selected Option:** *Option A: Smart Fitness Session Analyzer*

**Student:** Ola Nyvoll Negård
**Student Number:** 421967

## Description
The program simulates a fitness centres wearable-device pipeline. It uses the instructor supplied data_generator.py to produce a participant profile and a list of raw sensor observations for five scenarios. The program validates each observation, groups the valid ones into a training session, compares the session against the participants personal baseline, classifies the sessions intensity, and detects whether the participant is recovering toward the end of the session. The result is printed as a console report for each scenario. 

## Class design 
| Class | Responsibility |
|---|---|
| `Observation` | Represents a single measurement window. Validates itself on construction and exposes usability through a read-only `is_valid` property. |
| `Participant` | Represents a person and their baseline measurements. Can be built via `from_profile()` from the generator's profile dictionary. |
| `Session` | Composed of one `Participant` and a list of `Observation` objects,  the composition example in the design. |
| `SessionAnalyzer` | Analyzes a `Session`: summarizes, compares to baseline, detects recovery, classifies intensity, and returns a structured result dictionary. |

## Where composition, encapsulation, and class/static methods are demonstrated. 
**Composition:** Session is composed of one `Participant` and a list of `Observation`objects. This relationship is "has-a", not "is-a": a session doesn't behave like a participant or like an observation, it is built out of them: so composition is the natural fit here rather than inheritance. 
**Encapsulation:** `Participant`stores its baseline values in a protected attribute `_baseline`, only reachable thorugh the read-only `baseline` property(which returns a copy, so it cannot be mutated from outside) and update `update_baseline`. Similarly, `Observation`stores `_valid`and `_reasons`as protected attributes, exposed only through read-only `is_valid`and `reasons` properties, so a caller can enver overwrite the validation result directly. 
**Class method:** `Participant.from_profile()` is an alternative constructor that builds a `Participant`directly from the profile dictionary returned by `generate_fitness_data()`, instead of requiring the caller to unpack each field manually. 

## Assumptions and classification rules
- Validity ranges follow `Data_Description.md`: heart rate 35-205 bpm, temperature 25-42 degrees C, activity level and signal quality 0-1, skin response > 0. 
- A session needs at least 3 uasable observations to be classified; otherwise it is reported as insufficient data. 
- Recovery is detected by comparing the mean heart rate and activity level of the last third of a session against the middle third: both must drop by more than 10% for recovery to be flagged. 
- Activity-level thresholds for resting/moderate/high (0.25 and 0.70) were chosen by inspecting the actual output ranges of `generate_fitness_data()`for each scenario. 
- Classification order: recovery is checked first (since a session in recovery can have an average activity level similar to a moderate session, its the downward trend that distinguishes it), then resting/moderate/high activity based on average activity level and heart rate compared to baseline. 

## Installation and running instructions:
git clone https://github.com/olaneg/Mandatory-assignment
cd Mandatory-assignment
python3 main.py

**Run tests with:**
python3 tests.py

## Example output
SCENARIO: resting
Participant: P001
Usable observations: 12 / 12
Classification: resting
Explanation: Low activity level and heart rate close to or below baseline.

SCENARIO: moderate_activity
Participant: P002
Usable observations: 12 / 12
Classification: moderate activity
Explanation: Moderate activity level and elevated but controlled heart rate.

SCENARIO: high_activity
Participant: P003
Usable observations: 12 / 12
Classification: high activity
Explanation: High activity level and heart rate well above baseline.

SCENARIO: recovery
Participant: P004
Usable observations: 12 / 12
Classification: recovering
Explanation: Heart rate and activity level both declined near the end of the session.

SCENARIO: poor_quality
Participant: P005
Usable observations: 0 / 12
Classification: insufficient data
Explanation: Only 0 usable observation(s); need at least 3.