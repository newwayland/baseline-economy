from .household import BaselineEconomyHousehold
from .firm import BaselineEconomyFirm
from .schedule import ScheduleByType
from mesa.time import BaseScheduler, RandomActivation
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
    ):
        super().__init__()
        self.schedule = ScheduleByType(
            self,
            RandomActivation,
            [BaselineEconomyFirm, BaselineEconomyHousehold]
        )
        self.month_length = 21

        for i in range(num_firms):
            agent = BaselineEconomyFirm(
                i,
                self,
            )
            self.schedule.add(agent)

        for i in range(num_households):
            agent = BaselineEconomyHousehold(
                i,
                self,
            )
            self.schedule.add(agent)

        # example data collector
        self.datacollector = DataCollector()

        self.datacollector.collect(self)

    @property
    def firms(self) -> BaseScheduler:
        return self.schedule.by_type(BaselineEconomyFirm)

    @property
    def households(self) -> BaseScheduler:
        return self.schedule.by_type(BaselineEconomyHousehold)

    @property
    def num_firms(self) -> int:
        return self.firms.get_agent_count()

    @property
    def num_households(self) -> int:
        return self.households.get_agent_count()

    def is_month_start(self) -> bool:
        """
        Are we at the start of a month?
        Day 1, 22, 43, etc.
        """
        return self.schedule.steps % self.month_length == 1

    def is_month_end(self) -> bool:
        """
        Are we at the end of a month?
        Day 0, 21, 42, etc.
        """
        return self.schedule.steps % self.month_length == 0

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.schedule.step()
        self.datacollector.collect(self)
