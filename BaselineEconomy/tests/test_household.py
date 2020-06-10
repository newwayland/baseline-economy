from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.household import HouseholdConfig
import math
import pytest




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


def test_find_work():
    hh = initial_household()
    firm = hh.select_new_firm()
    firm.hire(hh)
    assert not hh.is_unemployed()
    hh.employer.quit_job(hh)
    assert hh.is_unemployed()
    for f in hh.model.firms.agents:
        f.has_open_position = True
        f.wage_rate = 1
        assert not f.workers
    # Should pick an employer as we're unemployed
    hh.look_for_work()
    assert not hh.is_unemployed()
    assert not hh.employer.has_open_position
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    current = hh.employer
    # Wages in firm aren't good enough. Should never move
    hh.look_for_work()
    assert hh.employer == current
    # Up the rates
    for f in hh.model.firms.agents:
        f.has_open_position = True
        f.wage_rate = 2
    current.wage_rate = 1
    current.has_open_position = True
    # Now we'll change firm
    hh.look_for_work()
    assert hh.employer != current
    # Finally quit and check queues are clear
    hh.employer.quit_job(hh)
    for f in hh.model.firms.agents:
        assert not f.workers


@pytest.mark.parametrize(
    "inv,price,cash,cons,finv,fliq,hliq",
    [
        (10, 1, 50, 5, 5, 5, 45),
        (2,  1, 50, 5, 0, 2, 48),
        (20, 1, 5, 20, 15, 5, 0)
    ]
)
def test_buy_goods(inv, price, cash, cons, finv, fliq, hliq):
    hh = initial_household()
    firm = hh.preferred_suppliers[0]
    firm.inventory = inv
    firm.goods_price = price
    hh.liquidity = cash
    hh.planned_daily_consumption = cons
    hh.buy_goods()
    assert firm.inventory == finv
    assert firm.liquidity == fliq
    assert firm.current_demand == min(inv, cons, cash // price)
    assert hh.liquidity == hliq
