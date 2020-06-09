from BaselineEconomy.household import (
    planned_consumption_amount,
    labour_supply
)
from BaselineEconomy.firm import (
    production_amount,
    wage_adjustment,
    price_adjustment,
    FirmConfig
)
import pytest
from random import Random


def test_consumption_integer_values():
    assert planned_consumption_amount(20, 8) == pytest.approx(2.28111)


def test_consumption_float_values():
    assert (
        planned_consumption_amount(1451.23, 45.235) == pytest.approx(22.6796)
    )


def test_labour_supply():
    assert labour_supply() == 1


def test_production_amount():
    assert production_amount(labour_supply()) == (
        labour_supply() * FirmConfig.lambda_val
    )


def test_wage_adjustment():
    assert (0 <= wage_adjustment(Random()) <= FirmConfig.delta)


def test_price_adjustment():
    assert (0 <= price_adjustment(Random()) <= FirmConfig.upsilon)


def positive_productivity_factor():
    assert FirmConfig.gamma > 0


def inventory_change_range_correct():
    assert (0 < FirmConfig.inventory_lphi < FirmConfig.inventory_uphi)


def price_change_range_correct():
    assert (1 < FirmConfig.goods_price_lphi < FirmConfig.goods_price_uphi)
