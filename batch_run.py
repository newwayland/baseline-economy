from BaselineEconomy.model import BaselineEconomyModel
from mesa.batchrunner import BatchRunner
from mesa.datacollection import DataCollector
import pandas as pd

br_params = {
    "num_households": [1000],
    "num_firms": [100],
    "household_liquidity": [100, 1000, 10000],
    "firm_liquidity": [0],
}

# Run for 6000 months plus 1000 months burn in
burn_in = 1000
run_length = 6000
total_steps = (run_length + burn_in) * 21


br = BatchRunner(
    BaselineEconomyModel,
    br_params,
    iterations=1,
    max_steps=total_steps,
    model_reporters={"Data Collector": lambda m: m.datacollector},
)

# Drop the burn in period from the data collection
if __name__ == "__main__":
    br.run_all()
    br_df = br.get_model_vars_dataframe()
    br_step_data = pd.DataFrame()
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = (
                br_df["Data Collector"][i]
                .get_model_vars_dataframe()
                .drop(list(range(burn_in)))
            )
            br_step_data = br_step_data.append(i_run_data, ignore_index=True)
    br_step_data.to_csv("BaselineEconomyModel_Step_Data.csv")
