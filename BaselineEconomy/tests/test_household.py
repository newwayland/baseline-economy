from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.household import HouseholdConfig
import math
import pytest


def initial_household():
    return BaselineEconomyModel(1, 10).households.agents[0]


def test_probability_check():
    hh = initial_household()
    assert hh.with_probability(1)
    assert not hh.with_probability(-0.1)


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
    # New unstepped household starts at end of previous month
    assert not hh.is_month_start()
    assert hh.is_month_end()
    assert hh.is_unhappy_at_work()


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


def test_work_status():
    hh = initial_household()
    assert hh.is_unemployed()
    assert hh.is_unhappy_at_work()
    hh.employer = hh.select_new_employer()
    assert not hh.is_unemployed()
    assert not hh.is_paid_too_little()
    hh.reservation_wage = 100
    assert not hh.is_unemployed()
    assert hh.is_paid_too_little()
    assert hh.is_unhappy_at_work()


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


def test_find_cheaper_vendor():
    hh = initial_household()
    for f in hh.preferred_suppliers:
        f.goods_price = 100
    hh.find_cheaper_vendor()
    assert any([o.goods_price != 100 for o in hh.preferred_suppliers])


def test_find_capable_vendor():
    hh = initial_household()
    assert not hh.blackmarked_firms
    org = hh.preferred_suppliers.copy()
    # Nobody blackmarked
    hh.find_capable_vendor()
    assert hh.preferred_suppliers == org
    assert not hh.blackmarked_firms
    hh.blackmark(hh.preferred_suppliers[0], 0)
    hh.blackmark(hh.preferred_suppliers[1], 1)
    assert len(hh.blackmarked_firms) == 2
    # Check weighted replace works
    hh.find_capable_vendor()
    assert hh.preferred_suppliers[0] == org[0]
    assert hh.preferred_suppliers[1] != org[1]
    assert len(hh.blackmarked_firms) == 2


def test_replaced_firm_is_skipped():
    hh = initial_household()
    hh.blackmark(hh.preferred_suppliers[1], 1)
    hh.preferred_suppliers[1] = hh.select_new_firm()
    org = hh.preferred_suppliers.copy()
    assert len(hh.blackmarked_firms) == 1
    hh.find_capable_vendor()
    assert hh.preferred_suppliers == org
    assert len(hh.blackmarked_firms) == 1
