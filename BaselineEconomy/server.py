"""
Configure visualization elements and instantiate a server
"""

from .model import BaselineEconomyModel  # noqa

from .ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

employed_chart = ChartModule(
    [
        {"Label": "Employed", "Color": "Black"},
        {"Label": "On Notice", "Color": "Red"}
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
        {"Label": "HH Savings", "Color": "Blue"}
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
        value=0,
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
        )
    }

server = ModularServer(
    BaselineEconomyModel,
    [employed_chart, firm_chart, price_chart, demand_chart, savings_chart,
        gini_chart],
    "Baseline Economy",
    model_params,
)
