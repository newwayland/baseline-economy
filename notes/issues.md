# Replication of Agent-based macroeconomics: A baseline model

## Bootstrap Issues (t=0)

- The initial values of the wage rate, goods price, inventory, and
  liquidity for Firms are not specified.

- The initial values of the reservation wage and liquidity for Households
  are not specified.

- Liquidity is exogenous to the model. 

- Equation `(5)` implies that the intial value of the wage rate has to
  be supplied and it must be greater than zero.

- Equation `(6)` and `(7)` imply that and intial value for the current demand
  has to be supplied and it must be greater than zero.

- Equation `(10)` implies that the intial value of the goods price has
  to be supplied and it must be greater than zero.

## Assumptions stated in paper

- The supply of liquidity is exogenous and unchanging

- Labour supply (l<sub>h</sub>) is fixed at 1 unit per household per tick

- A single model tick is a Day

- There are 21 Days is a Month

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

- Wages rises and cuts apply all workers in a firm immediately

- Workers can change jobs immediately, but are fired with one month's notice


## Issues

1.  Equation `(12)` seems redundant. Any x raised to a power y where `0 < y < 1` will always be less than x

2.  Since purchase is done daily, the amount of consumption in a day appears
    to be rounded down to an integer at that point and not before. Fractions
    of a good cannot be purchased. Monthly consumption changes per household
    are therefore in steps of 21.

3.  Blackmarked firms can already have been removed by the previous price competition step.

4.  The wage choice of the unemployed is ambiguous. It talks about a
    currently received wage, but as the household is unemployed they are
    not receiving a wage at that point. Other context suggests this should
    be “reserved wage”.

5.  Employed Households will jump jobs if they find a new job offering
    more than the minimum of their current wage rate or the reservation
    wage. The unemployed however will not take a job unless they get more
    than the reservation wage.

6.  If a worker is on notice and inventories are now too low, is the
    worker notice cancelled?

7.  In an open position exists and inventories are now too high, is a
    worker still given notice?

8.  Does an open position persist beyond the end of the month?

9.  The marginal cost calculation for firms is not specified. Is this
    the current marginal cost (relative to the labour supply of the current
    workers), or the expected marginal costs (relative to the labour supply
    of the current unemployed, or other people's workers), or something else.

10. The numeric types of the variables are not specified. Both monetary
    values and goods are usually whole units to avoid floating point
    rounding issues, but the value of Zeta in the household calibration
    suggests some sort of decimal type.

11. The average goods price calculation isn't specified. Is this a
    weighted mean taking into account current inventory (or prior
    inventory or projected inventory) or just a simple mean of the prices
    per firm? The former helps weight high prices.

12. A firm will not hire speculatively. Therefore if it ends up with
    zero inventory, demand and workers it effectively exits the economy

13. Only a worker paid less than their reservation wage searches for
    another job. A worker put on notice does not change their behaviour.

14. Unsatisfied demand isn't clearly specified. Is the shortfall from 95%
    of planned demand, or the shortfall from the planned demand. Is it
    availability, affordability or both?

## Workaround assumptions for issues

1.  Use equation 11

2.  The average price and planned monthly consumption is calculated as
    a floating point value, then integer divided by the month length to
    give an round number of items to buy a day. This is to maintain
    consistency with the algorithm described in the original paper.

3.  If the blackmark process picks a firm that has already been swapped
    out, leave it there. Don't look for another. It is assumed that the
    households need for vengeance has been satisfied as the firm has gone.

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
    (l<sub>h</sub)>) and the productivity technology factor(λ) is
    divided into the wage rate(w<sub>f</sub>>). This fits with the fixed
    labour supply assumption.

10. Liquidity and inventory are managed as integers. As are goods prices
    and wage rates.  Only whole amounts can be created and
    transferred. Zeta is scaled by 100 to compensate.  Precautionary
    buffers are rounded up. Purchases are rounded down. Intermediate
    calculations are floating point. This fits with the way those amounts
    are usually managed. The units are generally atomic at the point
    of transfer.

11. The goods prices from each firm are added up and divided by the number of
    firms.  It is assumed that the household only knows about prices of goods at
    the planning stage.

12. The demand for t=0 is given to the model exogenously at startup.

13. Workers continue to seach minimally for jobs when on notice. The
    inconsistency in the model is maintained.

14. The satisfaction amount is the whole number lower than 5% of the
    planned daily amount of goods. Unsatisfied demand is any 'remaining
    demand' above the satisfaction amount. This seems to fit with the
    description of the buying algorithm in the paper.
