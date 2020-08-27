from mesa import Agent
from typing import List, Tuple


# CONFIG

class FirmJGConfig:
    """
    Calibration Settings for the JobGuarantee Agent
    """

    # Amount of liquidity assigned to the JG at t=0
    # The initial JG float. An exogenous amount of money used to make
    # it look like the system isn't running a deficit.
    initial_liquidity = 0

    # Amount of inventory in each firm at t=0
    initial_inventory = 0

    # The base rate of the economy
    # How much labour is paid per day
    jg_day_rate = 50

    # Productivity multiple by which labour power
    # is turned into labour output
    # This is assumed to be lower in the JG
    # "Positive technology parameter"
    lambda_val = 1

    # Initial wage rate at t=0
    # Set to 21 * the labor day rate
    # Required due to Eq (5)
    # Value not stated in paper
    initial_wage_rate = jg_day_rate * lambda_val * 21

    # Price of goods at each firm at t=0
    # Required due to Eq (10)
    # Value not stated in paper
    initial_goods_price = jg_day_rate // lambda_val


# FUNCTIONS


def production_amount(labour_power: int) -> int:
    """
    Amount of labour output per unit of labour power
    """
    return FirmJGConfig.lambda_val * labour_power


class BaselineEconomyFirmJG(Agent):
    """
    Job Guarantee Agent

    The value of the liquidity parameter in the JG is the "deficit".
    The Job Guarantee buys workers off the floor of the market at the
    fixed day rate.

    Variables:

    liquidity: The initial JG float.
    goods_price: the price of each item in the inventory
    wage_rate: the fixed price the firm will pay for labour power
    """

    def __init__(
        self,
        unique_id: int,
        model,
        initial_liquidity: int,
        initial_goods_price: int,
        initial_wage_rate: int,
    ) -> None:
        """
        Customize the agent
        """
        super().__init__(unique_id, model)
        self.liquidity = initial_liquidity
        self.goods_price = initial_goods_price
        self.wage_rate = initial_wage_rate
        self.inventory = FirmJGConfig.initial_inventory
        self.current_demand = 0
        self.worker_on_notice = None
        self.workers = []
        self.has_open_position = True
        self.months_since_hire_failure = 0
        self.reset_monthly_stats()

    def month_start(self) -> None:
        """
        Run the month start firm procedures
        """
        self.reset_monthly_stats()
        # Reset monthly accumulators
        self.current_demand = 0

    def day(self) -> None:
        """
        Run the daily firm procedures
        """
        self.produce_output()

    def month_end(self) -> None:
        """
        Run the month end firm procedures
        """
        self.pay_wages()

# DAILY

    def produce_output(self) -> None:
        """
        Work out how much effort the firm can command and
        run it through the production process.
        Accumulate output in the firms inventory
        """
        labour_power = sum([o.labour_amount for o in self.workers])
        self.inventory += production_amount(labour_power)

# MONTH END

    def pay_wages(self) -> None:
        """
        Pay wages at the wage rate.
        The workers are simply marked up by the standard wage rate
        """
        num_workers = len(self.workers)
        for hh in self.workers:
            hh.liquidity += self.wage_rate
        self.liquidity -= num_workers * self.wage_rate

    def distribute_profits(self,
                           shareholding: List[Tuple],
                           total_shares: int) -> None:
        """
        No distributions from JG firm
        """
        pass

# HELPERS

    def reset_monthly_stats(self):
        """
        Reset the monthly recording attributes
        """
        self.raised_wage = False
        self.lowered_wage = False
        self.considered_price_change = False
        self.inventories_too_low = False
        self.inventories_too_high = False
        self.raised_goods_price = False
        self.lowered_goods_price = False

    def quit_job(self, worker) -> None:
        """
        Clear up when a worker leaves the firm
        """
        if self.worker_on_notice == worker:
            self.worker_on_notice = None
        self.workers.remove(worker)
        worker.employer = None

    def hire(self, worker) -> None:
        """
        Add worker to the list of current employees
        """
        self.workers.append(worker)
        worker.employer = self
        self.has_open_position = True

    def sell_goods(self, quantity, total_price) -> None:
        """
        Update inventory and demand
        then bank the cash
        """
        self.inventory -= quantity
        self.current_demand += quantity
        self.liquidity += total_price
