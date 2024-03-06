import numpy as np
from borbely import BorbelyModel
from config import configurations, default_params
from visualizations import plot_configurations, plot_sleep_wake_bars_for_all_configurations, plot_default_configuration

# Create an instance of the BorbelyModel class
model = BorbelyModel()

# Define the simulation parameters
ts = np.arange(0, 100, 0.5)
sleep_pressure_T0 = 0.1  # Initial sleep pressure. range: 0.0 - 1.0
wake_status_T0 = 1 # Initial wake status. Categorical Value: 1 for awake, 0 for asleep

# Call the function
#plot_default_configuration(BorbelyModel(default_params), ts, sleep_pressure_T0, wake_status_T0)

plot_configurations(configurations, model, ts, sleep_pressure_T0, wake_status_T0)

#plot_sleep_wake_bars_for_all_configurations(configurations, model, ts, sleep_pressure_T0, wake_status_T0)