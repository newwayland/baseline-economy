from BaselineEconomy.household import (
    planned_consumption_amount,
    labour_supply,
    HouseholdConfig
)
from BaselineEconomy.firm import (
    production_amount,
    wage_adjustment,
    price_adjustment,
    FirmConfig
)
import pytest
from random import Random


@pytest.mark.parametrize(
    "liquidity,ave_price,month_amt",
    [
        (20, 8, 2.28111),
        (1451.23, 45.235, 22.6796)
    ]
)
def test_consumption_values(liquidity, ave_price, month_amt):
    assert (
        planned_consumption_amount(liquidity, ave_price) ==
        pytest.approx(month_amt)
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

# Test that configs fit model constraints


def test_wage_decay_factor():
    assert (0 <= HouseholdConfig.alpha <= 1)


def test_positive_productivity_factor():
    assert FirmConfig.gamma > 0


def test_inventory_change_range_correct():
    assert (0 < FirmConfig.inventory_lphi < FirmConfig.inventory_uphi)


def test_price_change_range_correct():
    assert (1 < FirmConfig.goods_price_lphi < FirmConfig.goods_price_uphi)
