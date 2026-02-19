from economic_engine.engine import EconomicEngine


def test_usage_charges_incrementally():
    config = {
        "initial_capital": 10.0,
        "token_cost": 0.001,
        "api_call_cost": 0.02,
        "simulation_run_cost": 0.1,
        "hourly_burn_rate": 0.05,
        "investment": {"skill_upgrade_cost": 1.0},
        "reward_multipliers": {
            "door_to_doctor": 1.0,
            "length_of_stay": 1.0,
            "throughput": 1.0,
            "error_rate": 1.0,
        },
    }
    engine = EconomicEngine(config)
    econ = engine.initialize_agent("a1")

    first = engine.charge_usage(econ, tokens=1000, api_calls=10, simulation_runs=1)
    second = engine.charge_usage(econ, tokens=1000, api_calls=10, simulation_runs=1)

    assert round(first, 2) == 1.3
    assert round(second, 2) == 1.3
    assert round(econ.total_cost, 2) == 2.6
    assert round(econ.balance, 2) == 7.4
