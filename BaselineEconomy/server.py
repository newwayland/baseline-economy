"""
Configure visualization elements and instantiate a server
"""

from .model import BaselineEconomyModel  # noqa

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, BarChartModule
from mesa.visualization.UserParam import UserSettableParameter

employed_chart = ChartModule(
    [
        {"Label": "Employed", "Color": "Black"},
        # {"Label": "On Notice", "Color": "Red"}
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

agent_bar = BarChartModule(
    [{"Label": "Demand", "Color": "Blue"}],
    scope="agent",
)

household_chart = ChartModule(
    [
        {"Label": "Unsatisfied Demand", "Color": "Green"},
        # {"Label": "HH Liquidity", "Color": "Blue"}
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
    [employed_chart, household_chart],
    "Baseline Economy",
    model_params,
)
