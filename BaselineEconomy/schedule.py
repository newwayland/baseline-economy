from mesa.time import BaseScheduler
from mesa.model import Model
from mesa.agent import Agent
from typing import List


class ScheduleByType(BaseScheduler):
    """
    A scheduler which steps each type of agent in Class order.
    All type A, then all type B, etc.

    The enumeration order is the order of the supplied type list.

    Assumes that all agents have the required methods for
    the supplied scheduler
    """

    def __init__(
        self,
        model: Model,
        scheduler_type: type,
        agent_types: List[type]
    ) -> None:
        """
        Create New Typed Schedule
        """
        super().__init__(model)
        for t in agent_types:
            self._agents[t] = scheduler_type(model)

    def add(self, agent: Agent) -> None:
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """

        self._agents[type(agent)].add(agent)

    def remove(self, agent: Agent) -> None:
        """
        Remove all instances of a given agent from the schedule.
        """

        self._agents[type(agent)].remove(agent)

    def step(self) -> None:
        """
        Executes the step of each agent grouped by type in order

        Increment the day to start with so that the step number from
        within the agents starts at '1', not '0'

        """
        self.steps += 1
        self.time += 1
        for agent_class in self._agents.values():
            agent_class.()

    def get_agent_count(self) -> int:
        """ Returns the total number of agents """
        return sum([o.get_agent_count() for o in self._agents.values()])

    @property
    def agents(self) -> List[Agent]:
        """
        Returns a list of all the agents of all types
        """
        return list(
            [item for sublist in
                [o.agents for o in self._agents.values()]
                for item in sublist]
        )

    def by_type(self, aType: type) -> BaseScheduler:
        """
        Return the sub scheduler and its list of agents
        """
        return self._agents[aType]
