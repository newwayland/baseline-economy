from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.firm import (
    FirmConfig,
    production_amount
)


def initial_firm():
    return BaselineEconomyModel(3, 10).firms.agents[0]


def households(firm):
    return firm.model.households.agents


def test_probability_check():
    firm = initial_firm()
    assert firm.with_probability(1)
    assert not firm.with_probability(-0.1)


def test_initial_firm():
    firm = initial_firm()
    assert firm.wage_rate == FirmConfig.initial_wage_rate
    assert firm.liquidity == FirmConfig.initial_liquidity
    assert firm.worker_on_notice is None
    assert len(firm.workers) == 0
    # New unstepped firm starts at end of previous month
    assert not firm.is_month_start()
    assert firm.is_month_end()
    assert not firm.has_open_position
    assert not firm.should_lower_wage()
    assert not firm.should_raise_wage()
    assert firm.inventory == 0
    assert firm.inventory_ceiling() == 0
    assert firm.inventory_floor() == 0


def test_manage_workforce_hire():
    firm = initial_firm()
    firm.current_demand = 1
    hh = households(firm)
    firm.workers = hh.copy()
    firm.inventory = 0
    assert firm.worker_on_notice is None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Should hire due to low inventory
    firm.manage_workforce()
    assert firm.worker_on_notice is None
    assert firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Should maintain hire due to low inventory
    firm.manage_workforce()
    assert firm.worker_on_notice is None
    assert firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Hire maintained even if inventory stabilises
    firm.inventory = firm.current_demand
    firm.manage_workforce()
    assert firm.worker_on_notice is None
    assert firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Should cancel hire due to inventory run up
    # *and* give worker notice
    firm.inventory = 100
    firm.manage_workforce()
    assert firm.worker_on_notice is not None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh)


def test_manage_workforce_fire():
    firm = initial_firm()
    firm.current_demand = 1
    firm.inventory = 100
    assert firm.worker_on_notice is None
    assert not firm.has_open_position
    assert not firm.workers
    # Can't give notice if there isn't anybody
    firm.manage_workforce()
    assert firm.worker_on_notice is None
    assert not firm.has_open_position
    assert not firm.workers
    # Add some workers
    hh = households(firm)
    firm.workers = hh.copy()
    assert firm.worker_on_notice is None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Should give notice
    firm.manage_workforce()
    assert firm.worker_on_notice is not None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh)
    # Should fire and give notice
    firm.manage_workforce()
    assert firm.worker_on_notice is not None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh) - 1
    # Should cancel notice due to inventory collapse
    firm.inventory = 0
    firm.manage_workforce()
    assert firm.worker_on_notice is None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh) - 1


def test_wage_increase():
    firm = initial_firm()
    firm.wage_rate = 1
    firm.has_open_position = True
    assert firm.should_raise_wage()
    firm.set_wage_rate()
    assert (1 < firm.wage_rate <= 1 + FirmConfig.delta)


def test_wage_decrease():
    firm = initial_firm()
    firm.wage_rate = 1
    firm.months_since_hire_failure = FirmConfig.gamma
    assert firm.should_lower_wage()
    firm.set_wage_rate()
    assert (1 - FirmConfig.delta <= firm.wage_rate < 1)


def test_price_increase():
    firm = initial_firm()
    firm.wage_rate = 100
    firm.goods_price = 1
    firm.set_goods_price()
    assert (1 < firm.goods_price <= 1 + FirmConfig.upsilon)


def test_price_decrease():
    firm = initial_firm()
    firm.goods_price = 1
    firm.wage_rate = 1
    firm.set_goods_price()
    assert (1 - FirmConfig.upsilon <= firm.goods_price < 1)


def test_production_process():
    firm = initial_firm()
    for hh in firm.model.households.agents:
        firm.hire(hh)
    assert firm.inventory == 0
    firm.produce_output()
    expected_output = production_amount(
        sum([o.labour_amount for o in firm.model.households.agents])
    )
    assert firm.inventory == expected_output
    firm.produce_output()
    assert firm.inventory == 2 * expected_output


def test_pay_wages():
    firm = initial_firm()
    firm.wage_rate = 2
    for hh in firm.model.households.agents:
        hh.liquidity = 0
        firm.hire(hh)
    num_workers = len(firm.workers)
    firm.liquidity = 3 * num_workers
    # Pay full wage
    firm.pay_wages()
    assert firm.liquidity == num_workers
    assert all([o.liquidity == 2 for o in firm.workers])
    assert firm.wage_rate == 2
    # Pay half wages
    firm.pay_wages()
    assert firm.liquidity == 0
    assert all([o.liquidity == 3 for o in firm.workers])
    assert firm.wage_rate == 1


def test_hire_failure():
    firm = initial_firm()
    firm.check_for_hire_failure()
    assert firm.months_since_hire_failure == 1
    firm.check_for_hire_failure()
    assert firm.months_since_hire_failure == 2
    firm.has_open_position = True
    firm.check_for_hire_failure()
    assert firm.months_since_hire_failure == 0


def test_calculate_buffer():
    firm = initial_firm()
    firm.wage_rate = 40
    for hh in firm.model.households.agents:
        hh.liquidity = 0
        firm.hire(hh)
    num_workers = len(firm.workers)
    assert (firm.calculate_required_buffer() ==
            num_workers * firm.wage_rate * FirmConfig.chi)
    firm.wage_rate = 4
    # Should round up
    assert firm.calculate_required_buffer() == 2
    # No profits at all
    firm.distribute_profits()
    assert all([o.liquidity == 0 for o in firm.model.households.agents])
    # Still no profits
    firm.liquidity = 2
    firm.distribute_profits()
    assert all([o.liquidity == 0 for o in firm.model.households.agents])
    assert firm.liquidity == 2
    # Insufficient profits to distribute
    firm.liquidity += num_workers - 1
    firm.distribute_profits()
    assert all([o.liquidity == 0 for o in firm.model.households.agents])
    assert firm.liquidity == 2 + num_workers - 1


def test_distribute_profits():
    firm = initial_firm()
    firm.liquidity = 80
    for hh in firm.model.households.agents:
        hh.liquidity = 1
    firm.model.households.agents[-1].liquidity = 2
    firm.distribute_profits()
    assert all([o.liquidity >= 21 for o in firm.model.households.agents])
    assert firm.model.households.agents[-1].liquidity == 42


def test_marginal_cost():
    firm = initial_firm()
    firm.wage_rate = 63
    assert (
        firm.marginal_cost() ==
        firm.wage_rate / FirmConfig.lambda_val / firm.model.month_length
    )
