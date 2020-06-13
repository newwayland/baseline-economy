from mesa import Agent
import math


# CONFIG

class HouseholdConfig:
    """
    Calibration Settings for the Household Agent
    """

    # Reservation Wage assigned to each household at t=0
    # Value not stated in paper
    initial_reservation_wage = 0

    # Amount of liquidity assigned to each household at t=0
    # Value not stated in paper
    initial_liquidity = 0

    # Unemployed reservation wage decay rate
    # Value fixed at 10% reduction in paper
    wage_decay_rate = 0.9

    # Fraction of demand suppled that will satisfy the household desire
    # Value fixed at 95% in paper
    satisfaction_fraction = 0.95

    # Calibration values (Table 1)
    #
    # Fraction a new firms price has to be less than the
    # old firm before the new firm will be picked
    zeta = 0.01

    # Number of firms to search for work if unemployed
    beta = 5

    # Probability of searching for new work, if employed
    pi = 0.1

    # Decay rate for consumption expenditure function
    # in the range 0 < alpha < 1  Eq(11)
    alpha = 0.9

    # Number of firms in the preferred suppliers list
    # (Type A connections)
    num_preferred_suppliers = 7

    # Probability of looking for firm with cheaper prices
    psi_price = 0.25

    # Probability of dropping a firm that fails to supply
    psi_quant = 0.25


# FUNCTIONS

def planned_consumption_amount(
    current_liquidity: int,
    average_price: float
) -> float:
    """
    Table 2 - Consumption Function
    Calculate the amount of goods planned to be purchased over
    the month based upon the current amount of liquidity

    Shrink the amount by a scaling factor representing the amount of
    underconsumption (aka savings) the household undertakes.
    """
    return (current_liquidity / average_price) ** HouseholdConfig.alpha


# AGENT

class BaselineEconomyHousehold(Agent):
    """
    Household Agent

    Variables:

    reservation_wage: minimal claim on labour income
    liquidity: amount of monetary units household posseses
    preferred_suppliers: set of firms household prefers to buy from
    blackmarked_firms: firms that have failed to supply this month
    employer: The firm we're working for, None if unemployed
    current_demand: How many goods to buy each day
    """

    def __init__(
        self,
        unique_id: int,
        model,
        initial_liquidity: int
    ) -> None:
        """
        Customize the agent
        """
        super().__init__(unique_id, model)
        self.reservation_wage = HouseholdConfig.initial_reservation_wage
        self.liquidity = initial_liquidity
        self.preferred_suppliers = self.random.sample(
            model.firms,
            HouseholdConfig.num_preferred_suppliers
        )
        self.employer = None
        self.blackmarked_firms = []
        self.is_month_start = self.model.is_month_start
        self.is_month_end = self.model.is_month_end
        self.reset_monthly_stats()

    def month_start(self) -> None:
        """
        Run the month start household procedures
        """
        if not self.is_month_start():
            return
        self.reset_monthly_stats()
        # Look for cheaper vendors if household feels like it
        if self.with_probability(HouseholdConfig.psi_price):
            self.find_cheaper_vendor()
        # Dump a failed vendor if household feels like it
        if self.with_probability(HouseholdConfig.psi_quant):
            self.find_better_vendor()
        # Clear the blackmark list
        self.blackmarked_firms = []
        # Look for a job if household wants to
        if self.is_unhappy_at_work():
            self.look_for_new_job()
        self.plan_consumption()

    def day(self) -> None:
        """
        Run the daily household procedures
        """
        self.buy_goods()

    def month_end(self) -> None:
        """
        Run the month end household procedures
        """
        if not self.is_month_end():
            return
        self.adjust_reservation_wage()

# MONTH START

    def find_cheaper_vendor(self) -> None:
        """
        Look for a firm offereing cheaper goods
        """
        self.looked_for_cheaper_vendor = True
        # Pick an existing supplier to market test and calculate the
        # price the new supplier needs to beat
        supplier_index = range(0, len(self.preferred_suppliers) - 1)
        target_index = self.random.choice(supplier_index)
        change_price = (
            self.preferred_suppliers[target_index].goods_price *
            (1 - HouseholdConfig.zeta)
        )
        # Change supplier if the price is right
        new_firm = self.select_new_firm()
        if new_firm.goods_price < change_price:
            self.found_cheaper_vendor = True
            self.preferred_suppliers[target_index] = new_firm

    def find_better_vendor(self) -> None:
        """
        If the household has been let down look for new suppliers
        """
        # Nothing to do if all firms have delivered
        if not self.blackmarked_firms:
            return
        self.looked_for_better_vendor = True
        target_firm = self.select_blackmarked_firm()
        # The firm may already have been replaced by price competition
        # In which case 'index' will throw an error we need to catch
        try:
            target_index = self.preferred_suppliers.index(target_firm)
            self.preferred_suppliers[target_index] = self.select_new_firm()
            self.found_better_vendor = True
        except ValueError:
            self.vendor_already_replaced = True

    def look_for_new_job(self) -> None:
        """
        Look for another job
        Look harder if the household is unemployed or
        dissatisfied with the current job
        """
        # Look at more firms if household is unemployed
        self.looked_for_new_job = True
        num_searches = HouseholdConfig.beta if self.is_unemployed() else 1
        for _ in range(num_searches):
            potential_employer = self.select_new_employer()
            if self.is_acceptable_job_offer(potential_employer):
                if self.employer is not None:
                    self.employer.quit_job(self)
                potential_employer.hire(self)
                self.found_new_job = True
                return

    def plan_consumption(self) -> None:
        """
        Work out the daily consumption amount
        Calculates an integer amount
        """
        self.average_goods_price = sum(
            [o.goods_price for o in self.preferred_suppliers]
        ) / len(self.preferred_suppliers)
        try:
            self.planned_consumption = planned_consumption_amount(
                self.liquidity,
                self.average_goods_price
            )
            self.current_demand = (
                self.planned_consumption // self.model.month_length
            )
            self.planned_savings = (
                self.liquidity -
                self.planned_consumption * self.average_goods_price
            )
        except ZeroDivisionError:
            self.planned_consumption = math.inf
            self.current_demand = math.inf
            self.planned_savings = self.liquidity

# DAILY

    def buy_goods(self) -> None:
        """
        Buy goods from firms
        """
        # Put the preferred suppliers in a random order
        self.model.random.shuffle(self.preferred_suppliers)
        # Obtain the required amount of goods from
        # the preferred suppliers
        required_amount = self.current_demand
        satisfaction_amount = (math.floor(
                required_amount *
                (1 - HouseholdConfig.satisfaction_fraction)
        ))
        for vendor in self.preferred_suppliers:
            transaction_amount = self.check_vendor_stock(
                vendor,
                required_amount
            )
            self.transact(
                vendor,
                transaction_amount,
                transaction_amount * vendor.goods_price
            )
            required_amount -= transaction_amount
            # Stop checking firms if the household
            # has bought enough stuff
            if required_amount <= satisfaction_amount:
                return
        # Record unsatisfied demand
        self.unsatisfied_demand += required_amount - satisfaction_amount

# MONTH END

    def adjust_reservation_wage(self) -> None:
        """
        Make a note of the reservation wage
        which affects how intensely a household will look for a job
        """
        if self.is_unemployed():
            self.reservation_wage *= HouseholdConfig.wage_decay_rate
        else:
            self.reservation_wage = max(
                self.reservation_wage,
                self.employer.wage_rate
            )

# FIRM QUERIES

    @property
    def labour_amount(self):
        """
        Amount of labour power available from this household
        Just a delegation to the general expected labour supply value
        """
        return self.model.labour_supply

# HELPERS

    def reset_monthly_stats(self):
        """
        Reset the monthly recording attributes
        """
        self.unsatisfied_demand = 0
        self.demand_constraints_suffered = len(self.blackmarked_firms)
        # Reset decision flags
        self.looked_for_cheaper_vendor = False
        self.found_cheaper_vendor = False
        self.looked_for_better_vendor = False
        self.found_better_vendor = False
        self.looked_for_new_job = False
        self.found_new_job = False

    def check_vendor_stock(self, firm, required_amount: int) -> int:
        """
        Check the stock at a vendor and return how much the
        household can buy from them.
        Add them to the blackmark list if they can't supply
        what the household can demand
        """
        available_amount = firm.inventory
        affordable_amount = self.get_affordable_amount(firm)
        if (available_amount < required_amount and
                available_amount < affordable_amount):
            self.blackmark(firm, required_amount)
        return min(
            required_amount,
            affordable_amount,
            available_amount
        )

    def get_affordable_amount(self, firm) -> int:
        """
        Calculate how much the household can afford to buy
        """
        try:
            return self.liquidity // firm.goods_price
        except ZeroDivisionError:
            return math.inf

    def blackmark(self, firm, required_amount: int) -> None:
        """
        Add a firm to the blackmark list along with
        how short they were.
        A firm can end up with multiple records on this list
        """
        self.blackmarked_firms.append(
            (firm, required_amount - firm.inventory)
        )

    def transact(self, firm, quantity: int, total_price: int) -> None:
        """
        Buy the goods from the firm
        """
        firm.sell_goods(quantity, total_price)
        self.liquidity -= total_price

    def select_new_firm(self):
        """
        Select a new firm from the list of firms
        Filter out existing suppliers
        """
        firms = self.model.firms
        result = self.random.choice(firms)
        # If we've picked a current firm have another go
        while result in self.preferred_suppliers:
            result = self.random.choice(firms)
        return result

    def select_new_employer(self):
        """
        Select a new potential employer filter out current
        employer
        """
        firms = self.model.firms
        result = self.random.choice(firms)
        while self.employer is not None and result == self.employer:
            result = self.random.choice(firms)
        return result

    def select_blackmarked_firm(self):
        """
        Select a blackmarked firm - weighted by the extent
        of their failure to supply
        This involves unzipping the weights from the firms in the
        blackmark list and passing the sequences to the weighted
        random selector.

        Serial offenders may be on this list multiple times
        """
        choice_zip = zip(*self.blackmarked_firms)
        # Pull the lists off the zip
        firm_list = next(choice_zip)
        blackmarks = next(choice_zip)
        return self.random.choices(firm_list, weights=blackmarks)[0]

# QUERIES

    def is_unhappy_at_work(self) -> bool:
        """
        Does the household want to change jobs?
        """
        return (
            self.is_unemployed() or
            self.is_paid_too_little() or
            self.with_probability(HouseholdConfig.pi)
        )

    def is_paid_too_little(self) -> bool:
        """
        Is the household unhappy with their wage?
        """
        return self.employer.wage_rate < self.reservation_wage

    def is_acceptable_job_offer(self, new_employer) -> bool:
        """
        Is there an acceptable job offer on the table?
        The offer has to be more than the current or reservation wage to
        tempt people to move (including out of unemployment)
        """
        return (
            new_employer.has_open_position and
            (
                new_employer.wage_rate > self.reservation_wage or
                (self.employer is not None and
                 new_employer.wage_rate > self.employer.wage_rate)
            )
        )

    def is_unemployed(self) -> bool:
        """
        We're unemployed if we haven't got an Employer
        """
        return self.employer is None

    def with_probability(self, chance: float) -> bool:
        """
        Random check between 0 and 1
        """
        return self.random.random() < chance
