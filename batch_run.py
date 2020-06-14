from BaselineEconomy.model import BaselineEconomyModel
from mesa.batchrunner import BatchRunner
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt
import pandas as pd


def excess_demand_figure(df):
    plt.figure()
    df.plot.hist(
        bins=500,
        y="Unsatisfied Demand",
        density=True,
        histtype='step',
        align='left',
        legend=False,
        xlim=(0, 0.22),
        xticks=[0, 0.05, 0.1, 0.15, 0.2]
    )
    plt.title("Excess Demand")
    plt.xlabel("Unsatisfied demand (in %)")
    plt.ylabel("Probability Density Function")
    plt.savefig("/tmp/excess_demand.png")
    plt.close()


def employment_figure(df):
    plt.figure()
    df.plot.line(
        x="Year",
        y="Employed",
        legend=False,
        xticks=[0, 10, 20, 30, 40, 50],
        xlim=(0, 50),
        ylim=(950, 1000)
    )
    plt.title("Employment")
    plt.xlabel("Years")
    plt.ylabel("Employed households")
    plt.savefig("/tmp/employment.png")
    plt.close()


br_params = {
    "seed": [42],
    "num_households": [1000],
    "num_firms": [100],
    "household_liquidity": [5000],
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
    br_step_data.to_csv("/tmp/BaselineEconomyModel_Step_Data.csv")
    br_step_data["Year"] = (br_step_data.index.to_series() / 12)
    plt.close('all')
    excess_demand_figure(br_step_data)
    employment_figure(br_step_data)
