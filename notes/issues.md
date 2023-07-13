# Replication of Agent-based macroeconomics: A baseline model

## Bootstrap Issues (day=0)

- The initial values of the wage rate, goods price, inventory, and
  liquidity for Firms are not specified.

- The initial values of the reservation wage and liquidity for Households
  are not specified.

- Whether the household starts with an employer is not specified (Type
  B connection).

- It is implied, but not explicitly specified, that
  the household has a full initial set of 'n' preferred suppliers (Type
  A connections)

- Whether the household starts with a demand constraint is not specified. The
  month start procedure implies not.

- Equation `(5)` implies that the intial value of the wage rate has to
  be supplied and is expected to be greater than zero

- Equation `(6)` and `(7)` imply that an intial value for the current demand
  has to be supplied and it must be greater than zero.

- Equation `(10)` implies that the intial value of the goods price has
  to be supplied and it must be greater than zero.


## Assumptions derived from paper

- The supply of liquidity is exogenous and unchanging

- A single model tick is a Day,

- Labour supply (l<sub>h</sub>) is fixed at 1 unit per household per Day

- Productivity is fixed at a multiple of 3.

- There are 21 Days is a Month

- Month start is executed on day 1 of a month prior to the day process

- Month end is execture on day 21 of a month after the day process

- The model starts on day 1

- Households only work for one firm at a time (number of Type B
  connections = 1)

- Savings of firms are precautionary (no interest is paid on savings)

- Savings of households receive no interest, are a function of current
  consumption and relative to current liquidity

- Consumption is undertaken from preferred firms randomly regardless
  of price

- Profit is distributed to all households relative to their current
  liquidity (as a proxy for wealth)

- Unemployed reserved wage reduction is fixed at 10% per month

- Households in work will only look for jobs at no more than 1 other
  firm per month

- Unemployed Households look for jobs at no more than 5 firms per month

- Employees of a failing firm will take an immediate pay cut to keep
  their jobs. The wage rate is reduced to what the firm can afford

- Wages rises and cuts apply to all workers in a firm immediately

- Workers can change jobs immediately, but are fired with one month's notice

- Firms will hire the first Household that is prepared to take the
  offered wage rate, which means Households choose Firms, rather than
  Firms choosing Households.

- All workers are interchangeable (fully fungible) and their current
  employment condition (unemployed or hired) has no impact on whether
  a Firm will hire them.


## Issues

1.  Equation `(12)` seems redundant. It can only apply when the planned
    consumption is less than one unit of goods (not > 1 as stated in
    the paper). Since goods are necessarily atomic and discrete, not
    continuous, this will always be rounded idown to zero by the time
    the goods are purchased.

2.  Since purchases are done daily, the amount of consumption in a day
    appears to be rounded down to a whole number of units at that point.
    Logically fractions of a good cannot be purchased (if the
    units are too large to service your customers demands you would
    just split to a smaller integer base). Monthly consumption changes per
    household are therefore in steps of 21 units of goods.

3.  Blackmarked firms can already have been removed by the previous
    price competition step.

4.  The wage choice of the unemployed is ambiguous. The paper talks about a
    currently received wage, but as the household is unemployed they are
    not receiving a wage at that point. Other context suggests this should
    have been “reserved wage”.

5.  Employed Households will change jobs if they find a new job offering
    more than the minimum of their current wage rate or the reservation
    wage. The unemployed however will not take a job unless they get more
    than the reservation wage.

6.  If a worker is on notice and inventories are now too low, is the
    worker notice cancelled?

7.  In an open position exists and inventories are now too high, is a
    worker still given notice?

8.  Does an open position persist beyond the end of the month?

9.  The marginal cost calculation for firms is not specified. Is it
    the current marginal cost (relative to the labour supply of the current
    workers), or the expected marginal costs (relative to the labour supply
    of the current unemployed, or other people's workers), or something else?

10. The numeric types of the variables are not specified. Both monetary
    values and goods are usually managed as whole units to avoid floating
    point rounding issues.

11. The average goods price calculation isn't specified. Is this a
    weighted mean taking into account current inventory (or prior
    inventory or projected inventory) or just a simple mean of the prices
    per firm? The former would help weight high prices.

12. A firm will not hire speculatively. Therefore if it ends up with
    zero inventory, demand and workers it effectively exits the economy

13. Only a worker paid less than their reservation wage searches for
    another job. A worker put on notice does not change their behaviour.

14. Unsatisfied demand isn't clearly specified. Is the shortfall from 95%
    of planned demand, or the shortfall from the planned demand. Is it
    availability, affordability or both?

15. The end of month distribution process for firms is underspecified.
    At what point is the household 'current liquidity' for distribution
    calculated? Before wages, after wages, constantly after each firm
    has distributed (which would require random selection of firms)?

16. Is the order of the households randomly determined twice at the
    month start, once for the month start procedure and once for the
    day procedure, or is random order determined once and then used in
    both procedures?

17. The month start and month end processes run all firms before all
    households, whereas the day process runs all Households before
    Firms. This means households can only ever purchase from prior
    production, not current production and firms always end days and
    months with some unsold stock.

18. Although there is a crisis process in place for wages - which
    activates when the employing firm runs out of money - there isn't
    an equivalent 'fire sale' process for goods to get rid of excess
    inventory.

19. There is an assumption throughout the paper of infinitely divisible
    money and goods. Whereas money and goods are indivisible and wages are
    in whole units over a period of time. (In this case a month). This causes
    issues when the model drives prices down to unit levels.

20. Households select the firms they purchase from within their preferred
    supplier list randomly and not by lowest price first.

## Workaround assumptions for issues

1.  Use equation 11. The day algorithm includes an affordability check
    which constrains purchases to the budget available.

2.  The average price and planned monthly consumption is calculated as
    a floating point value, then integer divided by the month length to
    give a rounded down number of items to buy per day. This is to maintain
    consistency with the algorithm described in the paper.

3.  If the blackmark process picks a firm that has already been swapped
    out, stop the process. Don't look for another firm. It is assumed
    that the households need for vengeance has been satisfied as the
    firm has gone.

4.  The unmployed only take a position if the wage is greater than their
    current reservation wage. The inconsistency in the model is maintained.

5.  Workers will take less than their reservation wage, but the unemployed
    will not. The inconsistency in the model is maintained.

6.  If a hire position turns up while a worker is on notice, both states
    are cancelled. This is as would be expected given the turnaround in
    the firms fortunes.

7.  The hire position is cancelled, and a worker is given notice. This is
    as would be expected given the downturn in trade for the firm.

8.  Open positions persist month to month until filled or cancelled.

9.  The product of the month length(21), the labour supply
    (l<sub>h</sub>) and the productivity technology factor(λ) is
    divided into the wage rate(w<sub>f</sub>). This fits with the fixed
    labour supply assumption.

10. Liquidity and inventory are managed as integers. As are goods prices
    and wage rates.  Only whole amounts can be created and
    transferred. Precautionary buffers are rounded up. Purchases are
    rounded down. Intermediate calculations are floating point. This
    fits with the way these types of amounts are usually managed in
    programs. The units are treated as atomic at the point of transfer.

11. The goods prices from each firm are added up and divided by the
    number of firms.  It is assumed that the household only knows about
    prices of goods at the planning stage.

12. The demand for day=0 is given to the model exogenously at startup.

13. Workers continue to seach minimally for jobs when on notice. The
    inconsistency in the model is maintained.

14. The satisfaction amount is the whole number lower than 5% of the
    planned daily amount of goods. Unsatisfied demand is any 'remaining
    demand' above the satisfaction amount. This seems to fit with the
    description of the buying algorithm in the paper.

15. All firms first pay the wages. The 'current liquidity' is then
    calculated once and all firms use that weighting to distribute
    profits. Firms do not need to be randomised.  This requires two
    passes over the list of firms and fits with the text of the paper
    which appears to sequence wages first ('First, all firms pay their
    workers a wage')

16. The random order is determined once for the day procedure and the
    same order is used if the month start process needs to be run. This
    is ensures the household processing order changes only once per day.

17. The order is maintained to be consistent with the paper.

18. The processes are maintained to be consistent with the paper.

19. Wages can be driven to zero (Interns) but goods prices and goods can
    be no lower than 1. If the goods price drops to zero you get infinite
    demand and half a car isn't useful.

20. The order is maintained to be consistent with the paper.
