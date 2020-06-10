from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.firm import FirmConfig


def initial_firm():
    return BaselineEconomyModel(1, 10).firms.agents[0]


def household(firm):
    return firm.model.households.agents[0]


def test_initial_firm():
    firm = initial_firm()
    assert firm.wage_rate == FirmConfig.initial_wage_rate
    assert firm.liquidity == FirmConfig.initial_liquidity
    assert firm.worker_on_notice is None
    assert len(firm.workers) == 0
    assert firm.is_month_start()
    assert not firm.is_month_end()
    assert not firm.has_open_position
    assert not firm.should_lower_wage()
    assert not firm.should_raise_wage()


def test_give_notice():
    firm = initial_firm()
    firm.give_notice()
    assert firm.worker_on_notice is None
    hh = household(firm)
    firm.workers.append(hh)
    firm.give_notice()
    assert firm.worker_on_notice is not None
    firm.fire_worker()
    assert not firm.workers
    assert firm.worker_on_notice is None
