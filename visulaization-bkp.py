import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from borbely import BorbelyModel
from config import configurations, default_params

class Visualize:
    @staticmethod
    def plot_sleep_periods(ts_days, sleep_starts, sleep_ends, sol, ax):
        for start, end in zip(sleep_starts, sleep_ends):
            start_idx = (np.abs(ts_days - start)).argmin()
            end_idx = (np.abs(ts_days - end)).argmin()

            ax.plot([ts_days[start_idx]]*2, [0, sol.H[start_idx]], color='red', linestyle='--', alpha=0.5)
            ax.plot([ts_days[end_idx]]*2, [0, sol.H[end_idx]], color='green', linestyle='--', alpha=0.5)
            ax.plot(ts_days[start_idx], sol.H[start_idx], 'ro')  # red dot for sleep start
            ax.plot(ts_days[end_idx], sol.H[end_idx], 'go')  # green dot for sleep end

    @staticmethod
    def plot_sleep_awake_bars(ts_days, sleep_starts, sleep_ends, ax):
        # Fill the entire period with green (awake)
        ax.fill_between(ts_days, 0, 0.02, color='green', alpha=0.5)

        # Overlay the sleep periods in red
        for start, end in zip(sleep_starts, sleep_ends):
            start_idx = (np.abs(ts_days - start)).argmin()
            end_idx = (np.abs(ts_days - end)).argmin()
            ax.fill_between(ts_days[start_idx:end_idx], 0, 0.02, color='red', alpha=0.5)

        red_patch = mpatches.Patch(color='red', alpha=0.5, label='Sleep Period')
        green_patch = mpatches.Patch(color='green', alpha=0.5, label='Wake Period')

        return red_patch, green_patch

    @staticmethod
    def plot(sleep_data, ax):
        ts_days = sleep_data.time
        ax.plot(ts_days, sleep_data.H, label='Homeostatic Process - Sleep Pressure')

        # Calculate the circadian rhythm
        circadian_rhythm = sleep_data.calculate_circadian_rhythm(ts_days)
        ax.plot(ts_days, circadian_rhythm, label='Circadian Process')

        ax.plot(ts_days, sleep_data.lower, 'g--', label='Lower Sleep Bound')
        ax.plot(ts_days, sleep_data.upper, 'r--', label='Upper Sleep Bound')

        Visualize.plot_sleep_periods(ts_days, sleep_data.sleep_starts, sleep_data.sleep_ends, sleep_data, ax)
        red_patch, green_patch = Visualize.plot_sleep_awake_bars(ts_days, sleep_data.sleep_starts, sleep_data.sleep_ends, ax)

        max_hours = int(np.ceil(sleep_data.time[-1]))
        tick_locations = np.arange(0, max_hours + 1, 24)
        ax.set_xticks(tick_locations)

        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        ax.set_title("Borbely - Process S and Process C")
        ax.set_xlabel('Time (h)')
        ax.set_ylabel('Sleep Pressure')

def plot_configurations(configurations, model, ts, sleep_pressure_T0, wake_status_T0):
    # Create a figure and subplots
    fig, axs = plt.subplots(2, 3, figsize=(20, 10))

    # Loop over the configurations
    for i, config in enumerate(configurations):
        # Create a new model instance with the merged parameters
        model = BorbelyModel({**default_params, **config})

        # Simulate the sleep data
        sleep_data = model.simulate(ts, sleep_pressure_T0, wake_status_T0)

        # Plot the data in one of the subplots
        ax = axs[i // 3, i % 3]
        Visualize.plot(sleep_data, ax)

        # Add a title to the subplot
        ax.set_title(config['title'])

    # Create a separate figure for the legend
    fig_leg = plt.figure(figsize=(5, 3))

    # Create a single legend for the whole figure
    handles, labels = ax.get_legend_handles_labels()
    ax_leg = fig_leg.add_subplot(111)
    ax_leg.legend(handles, labels, loc='center', ncol=6)

    # Remove the axes from the legend figure
    ax_leg.axis('off')

    # Adjust the layout and show the figure
    plt.tight_layout()
    plt.show()

def plot_sleep_wake_bars_for_all_configurations(configurations, model, ts, sleep_pressure_T0, wake_status_T0):
    # Create a figure and subplots
    fig, axs = plt.subplots(len(configurations), 1, figsize=(10, 3 * len(configurations)))

    # Loop over the configurations
    for i, config in enumerate(configurations):
        # Create a new model instance with the merged parameters
        model = BorbelyModel({**default_params, **config})

        # Simulate the sleep data
        sleep_data = model.simulate(ts, sleep_pressure_T0, wake_status_T0)

        # Plot the sleep-wake bars in one of the subplots
        ax = axs[i]
        Visualize.plot_sleep_awake_bars(sleep_data.time, sleep_data.sleep_starts, sleep_data.sleep_ends, ax)

        # Add a title to the subplot
        ax.set_title(config['title'])

    # Adjust the layout and show the figure
    plt.tight_layout()
    plt.show()
