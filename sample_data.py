from data_generator import generate_fitness_data

_SCENARIO_SEEDS = {
    "resting": 1,
    "moderate_activity": 2,
    "high_activity": 3,
    "recovery": 4,
    "poor_quality": 5,
}

NUMBER_OF_WINDOWS = 12

SCENARIOS = {
    name: generate_fitness_data(
        participant_id=f"P00{i + 1}",
        scenario=name,
        seed=seed,
        number_of_windows=NUMBER_OF_WINDOWS,
    )
    for i, (name, seed) in enumerate(_SCENARIO_SEEDS.items())
}