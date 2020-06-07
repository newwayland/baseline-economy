from household import BaselineEconomyHousehold
from firm import BaselineEconomyFirm
from mesa.time import RandomActivation
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
            initial_reservation_wage=0,
            initial_offered_wage=0,
            firm_working_capital=0,
            initial_household_liquidity=0,
    ):
        super().__init__()
        self.households = RandomActivation(self)
        self.firms = RandomActivation(self)
        self.month_length = 21

        for i in range(num_firms):
            agent = BaselineEconomyFirm(
                i,
                self,
            )
            self.firms.add(agent)

        for i in range(num_households):
            agent = BaselineEconomyHousehold(
                i,
                self,
            )
            self.households.add(agent)

        # example data collector
        self.datacollector = DataCollector()

        self.datacollector.collect(self)

    @property
    def num_firms(self) -> int:
        return self.firms.get_agent_count()

    @property
    def num_households(self) -> int:
        return self.households.get_agent_count()

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.firms.step()
        self.households.step()
        self.datacollector.collect(self)
