from BaselineEconomy.model import BaselineEconomyModel
import pytest


@pytest.mark.parametrize(
    "households,firms",
    [
        (1000, 100),
        (10, 20)
    ])
def test_model_parameters(households, firms):
    parameter_model = (
        BaselineEconomyModel() if households == 1000 else
        BaselineEconomyModel(households, firms)
    )
    assert len(parameter_model.households) == households
    assert parameter_model.num_households == households
    assert len(parameter_model.firms) == firms
    assert parameter_model.num_firms == firms
    assert parameter_model.month_length == 21


def test_model_step():
    model = BaselineEconomyModel()
    old_firms = model.firms
    old_hh = model.households
    old_jg = model.job_guarantee
    # Model starts in month start mode
    assert old_firms[0].model.schedule.is_month_start()
    assert old_hh[0].model.schedule.is_month_start()
    assert old_jg.model.schedule.is_month_start()
    assert not old_firms[0].model.schedule.is_month_end()
    assert not old_hh[0].model.schedule.is_month_end()
    assert not old_jg.model.schedule.is_month_end()
    # Next 19 days should be neither start nor end
    for _ in range(model.month_length - 2):
        model.step()
        assert model.firms == old_firms
        assert model.households == old_hh
        assert model.job_guarantee == old_jg
        assert not old_firms[0].model.schedule.is_month_start()
        assert not old_hh[0].model.schedule.is_month_start()
        assert not old_jg.model.schedule.is_month_start()
        assert not old_firms[0].model.schedule.is_month_end()
        assert not old_hh[0].model.schedule.is_month_end()
        assert not old_jg.model.schedule.is_month_end()
    # Next day should be month end
    model.step()
    assert model.firms == old_firms
    assert model.households == old_hh
    assert model.job_guarantee == old_jg
    assert not old_firms[0].model.schedule.is_month_start()
    assert not old_hh[0].model.schedule.is_month_start()
    assert not old_jg.model.schedule.is_month_start()
    assert old_firms[0].model.schedule.is_month_end()
    assert old_hh[0].model.schedule.is_month_end()
    assert old_jg.model.schedule.is_month_end()
    # Then back to beginning of month again
    model.step()
    assert model.firms == old_firms
    assert model.households == old_hh
    assert model.job_guarantee == old_jg
    assert old_firms[0].model.schedule.is_month_start()
    assert old_hh[0].model.schedule.is_month_start()
    assert old_jg.model.schedule.is_month_start()
    assert not old_firms[0].model.schedule.is_month_end()
    assert not old_hh[0].model.schedule.is_month_end()
    assert not old_jg.model.schedule.is_month_end()
