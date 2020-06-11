# Replication of Agent-based Macroeconomics: A baseline Model

## Bootstrap Issues (t=0)

- The initial values of the wage rate, goods price, inventory, and liquidity for Firms are not specified.
- The initial values of the reservation wage and liquidity for Households are not specified.

## Assumptions
- Labour supply (l<sub>h</sub>) is fixed at 1 unit per household per tick
- A single model tick is a Day
- There are 21 Days is a Month
- Households only work for one firm at a time (number of Type B connections = 1)
- Liquidity in the system is fixed
- Savings of firms are precautionary (no interest is paid on savings)
- Savings of households receive no interest, are a function of current consumption and relative to current liquidity
- Consumption is undertaken from preferred firms randomly regardless of price
- Profit is distributed to all households relative to their current liquidity
- Unemployed reserved wage reduction is fixed at 10% per month
- Households in work will only look for jobs at no more than 1 other firm per month
- Unemployed Households look for jobs at no more than 5 firms per month
- Employees of a failing firm will take an immediate pay cut to keep their jobs. The wage rate is reduced to what the firm can afford
- Wages are raised pre-emptively for all workers if hiring fails
- Open positions persist month to month until filled

## Issues
- Equation `(12)` seems redundant. Any x raised to a power y where `0 < y < 1` will always be less than x
- Since purchase is done daily, the amount of consumption in a day appears
  to be rounded down to an integer at that point and not before. Fractions
  of a good cannot be purchased. Monthly consumption changes per household
  are therefore in steps of 21.
- Blackmarked firms can already have been removed by the previous price competition step.
- The wage choice of the unemployed is ambiguous. It talks about a
  currently received wage, but as the household is unemployed they are
  not receiving a wage at that point. Other context suggests this should
  be “reserved wage”.
- Employed Households will jump jobs if they find a new job offering
  more than the minimum of their current wage rate or the reservation
  wage. The unemployed however will not take a job unless they get more
  than the reservation wage.
- If a worker is on notice and inventories are now too low, is the worker notice cancelled?
- In an open position exists and inventories are now too high, is a worker still given notice?
- Does an open position persist beyond the end of the month?
- The numeric types of the variables are not specified. Both monetary
  values and goods are usually whole units to avoid floating point
  rounding issues, but the value of Zeta in the household calibration suggests some sort of decimal type
