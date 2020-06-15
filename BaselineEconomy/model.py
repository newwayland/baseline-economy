from .household import BaselineEconomyHousehold, HouseholdConfig
from .firm import BaselineEconomyFirm, FirmConfig
from .schedule import Scheduler
from mesa.datacollection import DataCollector
from mesa import Model
from typing import List, Tuple


class BaselineEconomyModel(Model):
    """
    A Baseline Agent-Based Macroeconomic Model


    which replicates the model described in:

    Lengnick, Matthias. (2013). Agent-based macroeconomics: A
    baseline model. Journal of Economic Behavior & Organization. 86.
    10.1016/j.jebo.2012.12.021.

    This version follows the paper as closely as possible

    """

    def __init__(
        self,
        num_households=1000,
        num_firms=100,
        household_liquidity=HouseholdConfig.initial_liquidity,
        firm_liquidity=FirmConfig.initial_liquidity,
        seed=None
    ):
        super().__init__()
        self.labour_supply = 1
        self.month_length = 21
        self.firms = [
            BaselineEconomyFirm(
                i + 1000,
                self,
                firm_liquidity
            ) for i in range(num_firms)]
        self.households = [
            BaselineEconomyHousehold(
                i,
                self,
                household_liquidity
            ) for i in range(num_households)]

        # Set up the scheduler from the model
        self.schedule = Scheduler(self)

        self.datacollector = DataCollector(
            model_reporters={
                "Employed": count_employed,
                "Unsatisfied Demand": percent_unsatisfied_demand,
                "On Notice": count_notice,
                "Inventory": sum_inventory,
                "Price": average_goods_price,
                "Wage": average_wage_rate,
                "HH Savings": sum_hh_savings,
                "Gini": compute_gini,
            },
        )

    @property
    def num_firms(self) -> int:
        """
        The number of firms in the model
        """
        return len(self.firms)

    @property
    def num_households(self) -> int:
        """
        The number of households in the model
        """
        return len(self.households)

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.schedule.step()
        # This is essentially a check before the next step
        # It's here to start collecting after the first
        # month has completed
        # if self.schedule.is_month_start():
        #     self.datacollector.collect(self)
        self.datacollector.collect(self)

    def calculate_shareholdings(self) -> (List[Tuple], int):
        """
        Calculate the 'shareholding' of firms based upon the current
        liquidty of the households.

        Return a tuple containing a list of holders and their imputed holding,
        and a total value for the holding.

        Each firm then distributes their profits to households proportinal
        to the holdings in this list
        """
        shareholding = [(o, o.liquidity) for o in self.households]
        return (shareholding, sum([x[1] for x in shareholding]))

# FUNCTIONS


def count_employed(model):
    """
    Number of households employed
    """
    return len(
        [hh for hh in model.households if hh.employer is not None]
    )


def count_notice(model):
    """
    Number of firms with worker on notice
    """
    return len(
        [f for f in model.firms if f.worker_on_notice is not None]
    )


def sum_expected_demand(model):
    """
    Total expected demand over month
    """
    return sum([hh.current_demand for hh in model.households]) * 21


def percent_unsatisfied_demand(model):
    """
    percentage of unsatisfied demand over expected demand
    """
    try:
        return (
            sum([hh.unsatisfied_demand for hh in model.households]) * 100
            / sum_expected_demand(model)
        )
    except ZeroDivisionError:
        return 0


def compute_gini(model):
    """
    Calculate the gini coefficient based upon household liquidity
    """
    try:
        x = sorted([hh.liquidity for hh in model.households])
        N = len(x)
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
        return 1 + (1 / N) - 2 * B
    except ZeroDivisionError:
        return 0


def sum_hh_savings(model):
    """
    How much money households have
    """
    return sum([hh.planned_savings for hh in model.households])


def sum_inventory(model):
    """
    Total stock in hand
    """
    return sum(
        [f.inventory for f in model.firms]
    )


def average_goods_price(model):
    """
    Average price of goods
    """
    prices = [f.goods_price for f in model.firms]
    return sum(prices) / len(prices)


def average_wage_rate(model):
    """
    Average wage rate
    """
    wage_rates = [f.wage_rate for f in model.firms]
    return sum(wage_rates) / len(wage_rates) / model.month_length
