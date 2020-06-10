from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.household import HouseholdConfig
import math


def initial_household():
    return BaselineEconomyModel(1, 10).households.agents[0]


def test_initial_household():
    hh = initial_household()
    assert len(
        hh.preferred_suppliers
    ) == HouseholdConfig.num_preferred_suppliers
    assert hh.reservation_wage == HouseholdConfig.initial_reservation_wage
    assert hh.liquidity == HouseholdConfig.initial_liquidity
    assert hh.employer is None
    assert hh.is_unemployed()
    assert len(hh.blackmarked_firms) == 0
    assert hh.is_month_start()
    assert not hh.is_month_end()
    assert not hh.is_happy_at_work()


def test_unemployed_adjust_wage():
    hh = initial_household()
    hh.reservation_wage = 100
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == 100 * HouseholdConfig.wage_decay_rate


def test_blackmarking():
    hh = initial_household()
    firm = hh.preferred_suppliers[0]
    hh.blackmarked_firms.append(
        (firm, 10)
    )
    bm_firm = hh.select_blackmarked_firm()
    assert bm_firm == firm


def test_select_new_firm():
    hh = initial_household()
    new_firm = hh.select_new_firm()
    assert new_firm not in hh.preferred_suppliers


def test_select_new_employer():
    hh = initial_household()
    first_employer = hh.select_new_employer()
    hh.employer = first_employer
    assert hh.employer is not None
    assert hh.select_new_employer() != first_employer


def test_initial_plan_consumption():
    hh = initial_household()
    hh.plan_consumption()
    assert hh.planned_daily_consumption == math.inf


def test_sacked():
    hh = initial_household()
    hh.employer = hh.select_new_firm()
    assert not hh.is_unemployed()
    hh.sacked()
    assert hh.is_unemployed()
