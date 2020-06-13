from .household import BaselineEconomyHousehold, HouseholdConfig
from .firm import BaselineEconomyFirm, FirmConfig
from mesa.time import BaseScheduler, StagedActivation
from mesa.datacollection import DataCollector
from mesa import Model


class BaselineEconomyModel(Model):
    """
    The model class holds the model-level attributes, manages the agents,
    and generally handles the global level of our model.
    There is only one model-level parameter: how many agents the model
    contains. When a new model is started, we want it to populate itself
    with the given number of agents.
    The scheduler is a special model component which controls the order
    in which agents are activated.
    """

    def __init__(
        self,
        num_households=1000,
        num_firms=100,
        household_liquidity=HouseholdConfig.initial_liquidity,
        firm_liquidity=FirmConfig.initial_liquidity
    ):
        super().__init__()
        self.schedule = StagedActivation(
            self,
            stage_list=["month_start", "day", "month_end"],
            shuffle=False,
        )
        self.month_length = 21
        self.firms = []
        self.households = []

        for i in range(num_firms):
            agent = BaselineEconomyFirm(
                i + 1000,
                self,
                firm_liquidity
            )
            self.schedule.add(agent)
            self.firms.append(agent)

        for i in range(num_households):
            agent = BaselineEconomyHousehold(
                i,
                self,
                household_liquidity
            )
            self.schedule.add(agent)
            self.households.append(agent)

        self.datacollector = DataCollector(
            model_reporters={
                "Employed": count_employed,
                "Unsatisfied Demand": percent_unsatisfied_demand,
                # "On Notice": count_notice,
                # "Inventory": sum_inventory,
                # "Price": average_goods_price,
                # "Wage": average_wage_rate,
                # "HH Liquidity": sum_hh_liquidity,
            },
        )

    @property
    def labour_supply(self) -> int:
        """
        Amount of labour power supplied by a household per day
        """
        return 1

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

    def is_month_start(self) -> bool:
        """
        Are we at the start of a month?
        Day 1, 22, 43, etc.
        """
        return (self.schedule.steps+1) % self.month_length == 1

    def is_month_end(self) -> bool:
        """
        Are we at the end of a month?
        Day 0, 21, 42, etc.
        """
        return (self.schedule.steps+1) % self.month_length == 0

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.schedule.step()
        if self.is_month_start():
            self.datacollector.collect(self)


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


def sum_hh_liquidity(model):
    """
    How much money households have
    """
    return sum([hh.liquidity for hh in model.households])


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
