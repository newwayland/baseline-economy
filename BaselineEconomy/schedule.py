# -*- coding: utf-8 -*-

from typing import List, Tuple


class Scheduler:
    """
    Bespoke scheduler to run the Baseline Economy by Class and Step
    according to the precise ordering in the paper.
    """

    def __init__(
        self,
        model
    ) -> None:
        """
        Initialise the scheduler with a reference to the model

        """
        # Instance variables
        self.model = model
        self.month_length = self.model.month_length
        self.month = 0
        self.day = 0
        self.steps = 0
        self.firms = self.model.firms.copy()
        self.households = self.model.households.copy()
        # Treat the JG as a firm for scheduling purposes
        self.firms.append(self.model.job_guarantee)

    def is_month_start(self) -> bool:
        """
        Are we at the start of a month?
        Day 1, 22, 43, etc.
        """
        return self.steps % self.month_length == 0

    def is_month_end(self) -> bool:
        """
        Are we at the end of a month?
        Day 0, 21, 42, etc.
        """
        return (self.steps+1) % self.month_length == 0

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

    def step(self) -> None:
        # Set the model day number
        self.day += 1
        # Shuffle the household list once per step
        self.model.random.shuffle(self.households)
        # Beginning of a month
        # Firms first
        if self.is_month_start():
            for firm in self.firms:
                firm.month_start()
            for hh in self.households:
                hh.month_start()
        # Lapse of a day
        # Households first
        for hh in self.households:
            hh.day()
        for firm in self.firms:
            firm.day()
        # End of a month
        # Firms first
        if self.is_month_end():
            # Pay Wages
            for firm in self.firms:
                firm.month_end()
            # Calculate householder shareholdings
            shareholder_details = self.calculate_shareholdings()
            # Distribute Profits
            for firm in self.firms:
                firm.distribute_profits(*shareholder_details)
            for hh in self.households:
                hh.month_end()
            self.month += 1
        self.steps += 1
