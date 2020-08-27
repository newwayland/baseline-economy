from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.household import (
    HouseholdConfig,
    planned_consumption_amount
)
import pytest


def initial_household():
    return BaselineEconomyModel(1, 10).households[0]


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
    assert not hh.on_job_guarantee()
    assert len(hh.blackmarked_firms) == 0
    assert hh.model.schedule.is_month_start()
    assert not hh.model.schedule.is_month_end()
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
    assert (
        hh.current_demand ==
        planned_consumption_amount(
            HouseholdConfig.initial_liquidity,
            hh.preferred_suppliers[0].goods_price
        ) // hh.model.month_length
    )


def test_job_guarantee():
    hh = initial_household()
    hh.reset_monthly_stats()
    assert hh.is_unemployed()
    assert not hh.on_job_guarantee()
    # Should pick job guarantee as we're unemployed
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = False
        f.wage_rate = f.model.job_guarantee.wage_rate
        assert not f.workers
    hh.look_for_new_job()
    assert hh.looked_for_new_job
    assert not hh.is_unemployed()
    assert hh.on_job_guarantee()
    assert hh.employer.has_open_position
    assert hh.is_unhappy_at_work()
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # Firms pay the same as Job Guarantee
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = True
        f.wage_rate = hh.reservation_wage
    # Will stay on Job Guarantee
    hh.look_for_new_job()
    assert hh.looked_for_new_job
    assert not hh.found_new_job
    assert not hh.is_unemployed()
    assert hh.on_job_guarantee()
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # Firms pay more than job guarantee
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = True
        f.wage_rate = f.model.job_guarantee.wage_rate + 1
    # Now we'll change firm
    hh.look_for_new_job()
    assert hh.looked_for_new_job
    assert hh.found_new_job
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # quit and check queues are clear
    hh.employer.quit_job(hh)
    for f in hh.model.firms:
        assert not f.workers
    assert not hh.model.job_guarantee.workers


def test_find_work():
    hh = initial_household()
    firm = hh.select_new_firm()
    firm.hire(hh)
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    #
    # Leaving a job when we haven't one should change nothing
    hh.employer.quit_job(hh)
    assert hh.is_unemployed()
    assert not hh.on_job_guarantee()
    # Should pick an employer as we're unemployed
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = True
        f.wage_rate = f.model.job_guarantee.wage_rate
        assert not f.workers
    hh.look_for_new_job()
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    assert not hh.employer.has_open_position
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # Wages in other firms aren't good enough. Should never move
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = True
        f.wage_rate = hh.reservation_wage
    current = hh.employer
    hh.look_for_new_job()
    assert hh.looked_for_new_job
    assert not hh.found_new_job
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # Firms pay more than job guarantee
    hh.reset_monthly_stats()
    for f in hh.model.firms:
        f.has_open_position = True
        f.wage_rate = f.model.job_guarantee.wage_rate + 1
    current.wage_rate = current.model.job_guarantee.wage_rate
    current.has_open_position = True
    # Now we'll change firm
    current = hh.employer
    hh.look_for_new_job()
    assert hh.looked_for_new_job
    assert hh.found_new_job
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    hh.adjust_reservation_wage()
    assert hh.reservation_wage == hh.employer.wage_rate
    #
    # quit and check queues are clear
    hh.employer.quit_job(hh)
    for f in hh.model.firms:
        assert not f.workers
    assert not hh.model.job_guarantee.workers


def test_work_status():
    hh = initial_household()
    assert hh.is_unemployed()
    assert not hh.on_job_guarantee()
    assert hh.is_unhappy_at_work()
    hh.employer = hh.select_new_employer()
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    assert not hh.is_paid_too_little()
    hh.reservation_wage = hh.employer.wage_rate + 1
    assert not hh.is_unemployed()
    assert not hh.on_job_guarantee()
    assert hh.is_paid_too_little()
    assert hh.is_unhappy_at_work()


@pytest.mark.parametrize(
    "inv,price,cash,cons,finv,fliq,hliq,jprice,jinv,kinv,jliq",
    [
        (10, 1, 50, 5, 5, 5, 45, 2, 0, 0, 0),
        (2,  1, 50, 5, 0, 2, 48, 2, 0, 0, 0),
        (20, 1, 5, 20, 15, 5, 0, 2, 0, 0, 0),
        (10, 1, 50, 15, 0, 10, 30, 2, 10, 5, 10),
        (10, 3, 50, 15, 5, 15, 15, 2, 10, 0, 20),
    ]
)
def test_buy_goods(inv, price, cash, cons, finv, fliq, hliq,
                   jprice, jinv, kinv, jliq):
    hh = initial_household()
    firm = hh.preferred_suppliers[0]
    jg = hh.model.job_guarantee
    firm.inventory = inv
    firm.goods_price = price
    jg.goods_price = jprice
    hh.liquidity = cash
    firm.liquidity = 0
    firm.current_demand = 0
    hh.current_demand = cons
    jg.inventory = jinv
    hh.buy_goods()
    assert firm.inventory == finv
    assert firm.liquidity == fliq
    if price < jprice:
        assert firm.current_demand == min(inv, cons, cash // price)
    assert jg.inventory == kinv
    assert jg.liquidity == jliq
    assert hh.liquidity == hliq


def test_find_cheaper_vendor():
    inflated_goods_price = 100000000
    hh = initial_household()
    for f in hh.preferred_suppliers:
        f.goods_price = inflated_goods_price
    hh.find_cheaper_vendor()
    assert any([o.goods_price != inflated_goods_price
                for o in hh.preferred_suppliers])


def test_find_better_vendor():
    hh = initial_household()
    assert not hh.blackmarked_firms
    org = hh.preferred_suppliers.copy()
    # Nobody blackmarked
    hh.find_better_vendor()
    assert hh.preferred_suppliers == org
    assert not hh.blackmarked_firms
    hh.blackmark(hh.preferred_suppliers[0], 0)
    hh.blackmark(hh.preferred_suppliers[1], 1)
    assert len(hh.blackmarked_firms) == 2
    # Check weighted replace works
    hh.find_better_vendor()
    assert hh.preferred_suppliers[0] == org[0]
    assert hh.preferred_suppliers[1] != org[1]
    assert len(hh.blackmarked_firms) == 2


def test_replaced_firm_is_skipped():
    hh = initial_household()
    hh.blackmark(hh.preferred_suppliers[1], 1)
    hh.preferred_suppliers[1] = hh.select_new_firm()
    org = hh.preferred_suppliers.copy()
    assert len(hh.blackmarked_firms) == 1
    hh.find_better_vendor()
    assert hh.preferred_suppliers == org
    assert len(hh.blackmarked_firms) == 1
