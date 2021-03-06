"""
Configure visualization elements and instantiate a server
"""

from .model import BaselineEconomyModel  # noqa

from .ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

personal_chart = ChartModule(
    [
        {"Label": "Employed", "Color": "Black"},
        {"Label": "On Notice", "Color": "Red"},
        {"Label": "Poverty Level", "Color": "Magenta"},
    ],
    data_collector_name='datacollector'
)
firm_chart = ChartModule(
    [
        {"Label": "Inventory", "Color": "Blue"}
    ]
)
price_chart = ChartModule(
    [
        {"Label": "Price", "Color": "Green"},
        {"Label": "Wage", "Color": "Black"}
    ]
)

demand_chart = ChartModule(
    [
        {"Label": "Unsatisfied Demand", "Color": "Green"},
    ]
)
savings_chart = ChartModule(
    [
        {"Label": "HH Savings", "Color": "Blue"},
        {"Label": "Total Liquidity", "Color": "Black"}
    ]
)
gini_chart = ChartModule(
    [
        {"Label": "Gini", "Color": "Red"}
    ]
)
model_params = {
    "num_households": 1000, "num_firms": 100,
    "household_liquidity": UserSettableParameter(
        "slider", "Household Starting Money",
        value=3200,
        min_value=0,
        max_value=50000,
        step=100
    ),
    "firm_liquidity": UserSettableParameter(
        "slider", "Firm Starting Money",
        value=0,
        min_value=0,
        max_value=50000,
        step=100
    ),
    "firm_goods_price": UserSettableParameter(
        "slider", "Initial Goods Price",
        value=27,
        min_value=1,
        max_value=1000,
        step=1
    ),
    "firm_wage_rate": UserSettableParameter(
        "slider", "Initial Daily Wage Rate",
        value=70,
        min_value=1,
        max_value=1000,
        step=1
    ),
    }

server = ModularServer(
    BaselineEconomyModel,
    [personal_chart, firm_chart, price_chart, demand_chart,
        savings_chart, gini_chart],
    "Baseline Economy",
    model_params,
)
