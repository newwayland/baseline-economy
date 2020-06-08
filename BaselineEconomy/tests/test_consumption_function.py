from BaselineEconomy.household import planned_consumption_amount
from pytest import approx


def test_integer_values():
    assert planned_consumption_amount(20, 8) == approx(2.28111)


def test_float_values():
    assert planned_consumption_amount(1451.23, 45.235) == approx(22.6796)
