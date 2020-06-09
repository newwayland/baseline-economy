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
    assert len(parameter_model.households.agents) == households
    assert parameter_model.num_households == households
    assert len(parameter_model.firms.agents) == firms
    assert parameter_model.num_firms == firms
    assert parameter_model.month_length == 21
