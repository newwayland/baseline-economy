from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.firm import (
    FirmConfig,
    production_amount
)


def initial_firm():
    return BaselineEconomyModel(3, 10).firms[0]


def households(firm):
    return firm.model.households


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
    assert firm.model.schedule.is_month_start()
    assert not firm.model.schedule.is_month_end()
    assert not firm.has_open_position
    assert not firm.should_lower_wage()
    assert not firm.should_raise_wage()
    assert firm.inventory == 0
    assert firm.inventory_ceiling() > firm.inventory
    assert firm.inventory_floor() > firm.inventory


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
    # Should give worker notice again due to inventory build up
    firm.inventory = 100
    firm.manage_workforce()
    assert firm.worker_on_notice is not None
    assert not firm.has_open_position
    assert len(firm.workers) == len(hh) - 1
    # Worker quits while on notice
    firm.quit_job(firm.worker_on_notice)
    assert firm.worker_on_notice is None
    assert len(firm.workers) == len(hh) - 2
    firm.manage_workforce()
    assert firm.worker_on_notice is not None
    assert len(firm.workers) == len(hh) - 2


price_multiple = 100 * FirmConfig.lambda_val * 21


def test_wage_increase():
    firm = initial_firm()
    firm.wage_rate = price_multiple
    firm.has_open_position = True
    assert firm.should_raise_wage()
    firm.set_wage_rate()
    assert (price_multiple
            < firm.wage_rate
            <= price_multiple*(1 + FirmConfig.delta))
    firm.wage_rate = 0
    assert firm.should_raise_wage()
    firm.set_wage_rate()
    assert firm.wage_rate == firm.model.job_guarantee.wage_rate
    assert firm.should_raise_wage()
    firm.set_wage_rate()
    assert firm.wage_rate > firm.model.job_guarantee.wage_rate


def test_wage_decrease():
    firm = initial_firm()
    firm.wage_rate = price_multiple
    firm.months_since_hire_failure = FirmConfig.gamma
    assert firm.should_lower_wage()
    firm.set_wage_rate()
    assert (price_multiple*(1 - FirmConfig.delta)
            <= firm.wage_rate
            < price_multiple)
    firm.wage_rate = 2
    assert firm.wage_rate == 2
    assert firm.should_lower_wage()
    firm.set_wage_rate()
    assert firm.wage_rate == 1
    assert firm.should_lower_wage()
    firm.set_wage_rate()
    assert firm.wage_rate == 0
    firm.set_wage_rate()
    assert firm.wage_rate == 0


def test_price_increase():
    firm = initial_firm()
    firm.inventory = 0
    firm.wage_rate = price_multiple*100
    firm.goods_price = price_multiple
    assert firm.goods_price <= firm.goods_price_ceiling()
    firm.set_goods_price()
    assert (price_multiple
            < firm.goods_price
            <= price_multiple*(1 + FirmConfig.upsilon))


def test_price_increase_limit():
    firm = initial_firm()
    firm.inventory = 0
    firm.wage_rate = 1
    firm.goods_price = price_multiple
    assert firm.goods_price > firm.goods_price_ceiling()
    firm.set_goods_price()
    assert firm.goods_price == price_multiple


def test_price_decrease():
    firm = initial_firm()
    firm.inventory = 10000
    firm.wage_rate = 1
    firm.goods_price = price_multiple
    assert firm.goods_price > firm.goods_price_floor()
    firm.set_goods_price()
    assert (price_multiple*(1 - FirmConfig.upsilon)
            <= firm.goods_price
            < price_multiple)


def test_price_decrease_limit():
    firm = initial_firm()
    firm.inventory = 10000
    firm.goods_price = price_multiple
    firm.wage_rate = price_multiple * 100
    assert firm.goods_price <= firm.goods_price_floor()
    firm.set_goods_price()
    assert firm.goods_price == price_multiple


def test_production_process():
    firm = initial_firm()
    for hh in firm.model.households:
        firm.hire(hh)
    assert firm.inventory == 0
    firm.produce_output()
    expected_output = production_amount(
        sum([o.labour_amount for o in firm.model.households])
    )
    assert firm.inventory == expected_output
    firm.produce_output()
    assert firm.inventory == 2 * expected_output


def test_pay_wages():
    firm = initial_firm()
    firm.wage_rate = 2
    for hh in firm.model.households:
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
    for hh in firm.model.households:
        hh.liquidity = 0
        firm.hire(hh)
    num_workers = len(firm.workers)
    assert (firm.calculate_required_buffer() ==
            num_workers * firm.wage_rate * FirmConfig.chi)
    firm.wage_rate = 4
    to_households = firm.model.schedule.calculate_shareholdings()
    # Should round up
    assert firm.calculate_required_buffer() == 2
    # No profits at all
    firm.distribute_profits(*to_households)
    assert all([o.liquidity == 0 for o in firm.model.households])
    # Still no profits
    firm.liquidity = 2
    firm.distribute_profits(*to_households)
    assert all([o.liquidity == 0 for o in firm.model.households])
    assert firm.liquidity == 2
    # Insufficient profits to distribute
    firm.liquidity += num_workers - 1
    firm.distribute_profits(*to_households)
    assert all([o.liquidity == 0 for o in firm.model.households])
    assert firm.liquidity == 2 + num_workers - 1


def test_distribute_profits():
    firm = initial_firm()
    firm.liquidity = 80
    for hh in firm.model.households:
        hh.liquidity = 1
    firm.model.households[-1].liquidity = 2
    to_households = firm.model.schedule.calculate_shareholdings()
    firm.distribute_profits(*to_households)
    assert all([o.liquidity >= 21 for o in firm.model.households])
    assert firm.model.households[-1].liquidity == 42


def test_marginal_cost():
    firm = initial_firm()
    firm.wage_rate = 63
    assert (
        firm.marginal_cost() ==
        firm.wage_rate / FirmConfig.lambda_val / firm.model.month_length
    )
