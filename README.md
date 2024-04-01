# Prosperity-Trader
This is the repo to test and develop trading algorithm for the IMC prosperity trading challenge.

## Setup
Create a conda environment `trader` and activate the environment with the following command:
```bash
conda create -n trader python=3.12
conda activate trader
```
Install the required packages:
```bash
conda install pandas numpy jsonpickle matplotlib ipykernel
```
Note that `matplotlib` is for visualization, `ipykernel` is required to run the jupyter notebook in the conda environment, neither of them are not required for the trading simulation.