from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.firm import FirmConfig


def initial_firm():
    return BaselineEconomyModel(1, 10).firms.agents[0]


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
