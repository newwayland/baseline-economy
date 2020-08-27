from BaselineEconomy.model import BaselineEconomyModel
from BaselineEconomy.firm_jg import (
    FirmJGConfig,
    production_amount
)


def job_guarantee():
    return BaselineEconomyModel(3, 10).job_guarantee


def households(firm):
    return firm.model.households


def test_job_guarantee():
    firm = job_guarantee()
    assert firm.wage_rate == FirmJGConfig.initial_wage_rate
    assert firm.liquidity == FirmJGConfig.initial_liquidity
    assert firm.worker_on_notice is None
    assert len(firm.workers) == 0
    assert firm.model.schedule.is_month_start()
    assert not firm.model.schedule.is_month_end()
    assert firm.has_open_position
    assert firm.inventory == 0


def test_production_process():
    firm = job_guarantee()
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
    firm = job_guarantee()
    for hh in firm.model.households:
        hh.liquidity = 0
        firm.hire(hh)
    # Still a job available
    assert firm.has_open_position
    # Pay full wage
    firm.pay_wages()
    num_workers = len(firm.workers)
    assert firm.wage_rate == FirmJGConfig.initial_wage_rate
    assert firm.liquidity == - firm.wage_rate * num_workers
    assert all([o.liquidity == firm.wage_rate for o in firm.workers])
    # Everybody leaves
    for hh in firm.model.households:
        firm.quit_job(hh)
    assert not firm.workers
