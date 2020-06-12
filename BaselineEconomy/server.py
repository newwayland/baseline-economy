"""
Configure visualization elements and instantiate a server
"""

from .model import BaselineEconomyModel  # noqa

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule


chart_element = ChartModule(
    [
        {"Label": "Employed", "Color": "Black"}
    ],
    data_collector_name='household_datacollector'
)

model_kwargs = {"num_households": 1000, "num_firms": 100}

server = ModularServer(
    BaselineEconomyModel,
    [chart_element],
    "Baseline Economy",
    model_kwargs,
)
