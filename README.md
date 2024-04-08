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
Note that `matplotlib` is for visualization, `ipykernel` is required to run the jupyter notebook in the conda environment, neither of them is required for the trading simulation.

**Example**
An example [trader.py](trader.py) is provided in the repo.
The file is an empty skeleton and does not have any trading strategy coded up.

:warning: **People could make their own copy of the file as `trader_<name>.py` and implement their own trading strategy.**

## Use the Visualizer and Back-tester
The skeleton file contains the necessary modification to use the [IMC Prosperity 2 Visualizer](https://jmerle.github.io/imc-prosperity-2-visualizer/).

To use the visualizer, follow the steps below:
1. Modify the `trader_<name>.py` file to implement your own trading strategy.
2. Upload the `trader_<name>.py` to the Prosperity server.
3. After the server finishes the simulation, download the log file from the server and upload it to the visualizer.
4. Check out the performance of your trading strategy there!

To use the [backtester](https://github.com/jmerle/imc-prosperity-2-backtester), follow the online instructions to install the package and run in the terminal.
Note that the code only does the order matching on the existing orders in `order_depth`, but in the real prosperity server, the order matching can also happen with hidden orders with virtual bots.

The backtester is compiled to load data from some `.csv` files stored under `resources/` folder which are extracted from prosperity log files.
In principle, with some modification to the raw code, it could also be used to validate the performance on a subset of the data.

The log files generated from the prosperity server are stored in the `shared_data/` folder such that the whole team can visualize the performance of trading strategies from different developers.

## Use `traderData` to store data between iterations
The algorithm needs some data to make trading decisions, which should be stored in the `traderData` object to make sure it is persistent between iterations.

All user data is stored in `traderData` and needs to be serialized to `string` object before returning to the simulator.
```python
import jsonpickle
traderData = jsonpickle.encode(traderData)
```
To use the `traderData` in the next iteration, deserialize the `string` object back to `traderData`.
```python
traderData = jsonpickle.decode(traderData)
```