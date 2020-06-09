from mesa import Agent
from random import Random


# CONFIG

class FirmConfig:
    """
    Calibration Settings for the Firm Agent
    """

    # Amount of liquidity assigned to each firm at t=0
    # Value not stated in paper
    initial_liquidity = 0

    # Price of goods at each firm at t=0
    # Value not stated in paper
    initial_goods_price = 0

    # Amount of inventory in each firm at t=0
    # Value not stated in paper
    initial_inventory = 0

    # Initial wage rate at t=0
    # Value not stated in paper
    initial_wage_rate = 0

    # Number of months of filled positions
    # before wage will be reduced
    gamma = 24

    # Upper bound for the wage adjustment
    delta = 0.019

    # Range that inventories can be maintained
    # relative to demand
    inventory_uphi = 1
    inventory_lphi = 0.25

    # Range that prices can be marked up over
    # costs
    goods_price_uphi = 1.15
    good_price_lphi = 1.025

    # Upper bound for the price adjustment
    upsilon = 0.02

    # Probability of changing the goods price
    theta = 0.75

    # Productivity multiple by which labour power
    # is turned into labour output
    #
    # "Positive technology parameter"
    lambda_val = 3

    # Percentage of income to reserve to cover bad times
    chi = 0.1


# FUNCTIONS


def production_amount(labour_power: int) -> int:
    """
    Amount of labour output per unit of labour power
    """
    return FirmConfig.lambda_val * labour_power


def wage_adjustment(rand_generator: Random) -> float:
    """
    Delta percentage amount to change the wage up or down
    """
    return rand_generator.uniform(0, FirmConfig.delta)


def price_adjustment(rand_generator: Random) -> float:
    """
    Delta percentage amount to change the price up or down
    """
    return rand_generator.uniform(0, FirmConfig.upsilon)


class BaselineEconomyFirm(Agent):
    """
    Firm Agent

    Variables:

    liquidity: amount of monetary units firm posseses
    """

    def __init__(self, unique_id, model) -> None:
        """
        Customize the agent
        """
        super().__init__(unique_id, model)
        self.liquidity = FirmConfig.initial_liquidity
        self.goods_price = FirmConfig.initial_goods_price
        self.wage_rate = FirmConfig.initial_wage_rate
        self.inventory = FirmConfig.initial_inventory

    def step(self) -> None:
        """
        Run the firm step processes
        """
        if self.model.is_month_start():
            self.month_start()
        self.day()
        if self.model.is_month_end():
            self.month_end()

    def month_start(self) -> None:
        """
        Run the month start firm procedures
        """
        

    def day(self) -> None:
        """
        Run the daily firm procedures
        """
        pass

    def month_end(self) -> None:
        """
        Run the month end firm procedures
        """
        pass

# QUERIES

    def is_month_start(self) -> bool:
        """
        Are we at the start of a month?
        """
        return self.model.firms.steps % self.model.month_length == 0

    def is_month_end(self) -> bool:
        """
        Are we at the end of a month?
        """
        return (self.model.firms.steps + 1) % self.model.month_length == 0
