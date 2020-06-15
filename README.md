# Agent-based Macroeconomics: A baseline model

![Python package](https://github.com/newwayland/baseline-economy/workflows/Python%20package/badge.svg)

This repo is a replication of the baseline model described in:

Lengnick, Matthias. (2013). Agent-based macroeconomics: A baseline model. Journal of Economic Behavior & Organization. 86. [10.1016/j.jebo.2012.12.021.](https://doi.org/10.1016/j.jebo.2012.12.021)

using the [Project Mesa modelling framework](https://github.com/projectmesa/mesa), to replicate the results of the paper as [closely as possible](notes/issues.md)

## Running an Interactive Sesion

- Clone the repo into a directory.
- Install the dependencies with `pipenv install`
- Run the server with `pipenv run python run.py`
- Adjust the sliders to choose the amount of 'exogenous money' to supply to each entity
- Click the 'reset' button to register the values
- Click 'Start' or 'Step' to advance the model
- Play about with the starting values and see if you can stop the economy inflating or deflating

## Running the mode in batch mode

The interactive session is relatively slow. To get thousands of cycles use the batch runner

- Clone the repo into a directory
- Install the dependencies with `pipenv install`
- Run the server with `pipenv run python batch_run.py`
- By default this will do a 7000 month run and save the statistics and
  graphs into the `/tmp` directory.
- Edit the `batch_run.py` file to change the model run parameters.
