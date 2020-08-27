# Alterations to model to support Job Guarantee

## Overview

A guaranteed job is the default job in the economy. If you assume that
everybody is working on the guaranteed job, then the output from those
hours must be sufficient to ensure that everybody reaches the poverty line.

There's a certain amount of circularity there, in that the output produced by
all the labour may define the poverty line if capital development is weak. 

The alteration to the baseline model reflects that. The assumption, in
line with the capital friendly thinking within the model, rather than
necessarily in line with the real world, is that work on the guaranteed
job won't be as productive as work elsewhere.

The Lambda "technology parameter" is therefore set to 1 rather than 3.

The guaranteed job wage rate is set arbitrarily to 10 units per day,
and since the production factor is 1 the goods price is set to 10 units
for guaranteed job output. The poverty line is therefore 1 unit of goods
per day.

The guaranteed job always offers a vacancy, never varies its price or
its wage rate.

Within the model the guaranteed job is Firm 101. Every person knows about
the output from the guaranteed job and therefore maintains an additional
Type A (goods purchase) relationship with Firm 101. 

Similarly during a search for a new job, an individual will always
consider the guaranteed job in addition to the private firms they have
chosen to apply to.

This means the unemployed continue to exists until their reservation
wage drops below the guaranteed job wage. Then they will join Firm 101

## Algorithm alterations

### Beginning of Month

Firm 101 undertakes does no wage or price change. Both remain fixed. There
is always an open position and nobody is ever fired.

An employee of Firm 101 is assumed to be unsatisfied with the position
and will search for a new job on that basis.

Once a household searching for a job has completed looking through
private firms, it will perform an additional check against Firm 101.

The trading connection changes only apply to the list of private preferred
suppliers (type A connections). Firm 101 is excluded. This represents
the view that Firm 101 is expected to be the last resort supplier.

Similarly household consumption planning continues to be done based
upon the prices of the private preferred suppliers. If private supply
falters then households will have to dip into their savings to purchase
what they require from firm 101. This refects the rachet effect - it's
easier to increase consumption than cut it.

### Lapse of Day

Firm 101 is added to the list of private prefered suppliers (type A
connections). Households visit the firms in price order - lowest first.

Firm 101 produces as any other firm, but with its own parameters

### End of Month

Firm 101 pays the fixed wage to all its employees by simply marking up
the worker's liquidity. Similarly any liquidity received by firm 101
for goods is discarded (taxed). This process makes the money supply
endogenous within the model.


