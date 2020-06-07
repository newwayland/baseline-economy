from mesa import Agent


class FirmConfig:
    """
    Calibration Settings for the Firm Agent
    """

    # Amount of liquidity assigned to each firm at t=0
    # Value not stated in paper
    initial_liquidity = 0


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
        pass

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
