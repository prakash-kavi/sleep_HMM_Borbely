import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from borbely import BorbelyModel
from config import configurations, default_params

class SleepWakeCyclePlotter:
    def __init__(self, plot_vertical_dashed_lines=True, plot_dots_at_sleep_starts_ends=True, plot_sleep_awake_bars=True):
        self.plot_vertical_dashed_lines = plot_vertical_dashed_lines
        self.plot_dots_at_sleep_starts_ends = plot_dots_at_sleep_starts_ends
        self.plot_sleep_awake_bars = plot_sleep_awake_bars

    def plot(self, ts_days, sleep_starts, sleep_ends, sol, ax):
        if self.plot_vertical_dashed_lines:
            self._plot_vertical_dashed_lines(ts_days, sleep_starts, sleep_ends, sol, ax)
        if self.plot_dots_at_sleep_starts_ends:
            self._plot_dots_at_sleep_starts_ends(ts_days, sleep_starts, sleep_ends, sol, ax)
        if self.plot_sleep_awake_bars:
            self._plot_sleep_awake_bars(ts_days, sleep_starts, sleep_ends, ax)

    @staticmethod
    def _plot_vertical_dashed_lines(ts_days, sleep_starts, sleep_ends, sol, ax):
        for start, end in zip(sleep_starts, sleep_ends):
            start_idx = (np.abs(ts_days - start)).argmin()
            end_idx = (np.abs(ts_days - end)).argmin()

            ax.plot([ts_days[start_idx]]*2, [0, sol.upper[start_idx]], color='red', linestyle='--', alpha=0.5)
            ax.plot([ts_days[end_idx]]*2, [0, sol.lower[end_idx]], color='green', linestyle='--', alpha=0.5)

    @staticmethod
    def _plot_dots_at_sleep_starts_ends(ts_days, sleep_starts, sleep_ends, sol, ax):
        for start, end in zip(sleep_starts, sleep_ends):
            start_idx = (np.abs(ts_days - start)).argmin()
            end_idx = (np.abs(ts_days - end)).argmin()

            # Plot the red dot at the intersection of sleep pressure and the upper bound
            ax.plot(ts_days[start_idx], sol.upper[start_idx], 'ro')  
            
            # Plot the green dot at the intersection of sleep pressure and the lower bound
            ax.plot(ts_days[end_idx], sol.lower[end_idx], 'go')  

    @staticmethod
    def _plot_sleep_awake_bars(ts_days, sleep_starts, sleep_ends, ax):
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

class CircadianProcessPlotter:
    @staticmethod
    def plot(sleep_data, ax):
        ts_days = sleep_data.time
        ax.plot(ts_days, sleep_data.H, label='Homeostatic Process - Sleep Pressure')

        # Calculate the circadian rhythm
        circadian_rhythm = sleep_data.calculate_circadian_rhythm(ts_days)
        ax.plot(ts_days, circadian_rhythm, label='Circadian Process')

        ax.plot(ts_days, sleep_data.lower, 'g--', label='Lower Sleep Bound')
        ax.plot(ts_days, sleep_data.upper, 'r--', label='Upper Sleep Bound')

        # Removed the call to SleepWakeCyclePlotter.plot_sleep_periods

        max_hours = int(np.ceil(sleep_data.time[-1]))
        tick_locations = np.arange(0, max_hours + 1, 24)
        ax.set_xticks(tick_locations)

        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        ax.set_title("Borbely - Process S and Process C")
        ax.set_xlabel('Time (h)')
        ax.set_ylabel('Sleep Pressure')

class StatisticalAnalysisPlotter:
    @staticmethod
    def calculate_statistics(sleep_data):
        # Add code here to calculate statistics like average sleep duration, standard deviation, etc.
        # Return the results as a dictionary or a custom data structure
        pass

    @staticmethod
    def plot_statistics(statistics, ax):
        # Add code here to plot the calculated statistics
        pass

class Visualize:
    def __init__(self, sleep_wake_cycle_plotter):
        self.sleep_wake_cycle_plotter = sleep_wake_cycle_plotter
        self.circadian_process_plotter = CircadianProcessPlotter()
        self.statistical_analysis_plotter = StatisticalAnalysisPlotter()

    def plot_all(self, sleep_data, ax):
        self.sleep_wake_cycle_plotter.plot(sleep_data.time, sleep_data.sleep_starts, sleep_data.sleep_ends, sleep_data, ax)
        self.circadian_process_plotter.plot(sleep_data, ax)
        # Calculate statistics and plot them
        statistics = self.statistical_analysis_plotter.calculate_statistics(sleep_data)
        self.statistical_analysis_plotter.plot_statistics(statistics, ax)
        
def plot_default_configuration(model, ts, sleep_pressure_T0, wake_status_T0):
    # Create a figure for default configuration
    fig, ax = plt.subplots(figsize=(10, 6))
    sleep_wake_cycle_plotter = SleepWakeCyclePlotter(plot_vertical_dashed_lines=True, plot_dots_at_sleep_starts_ends=True, plot_sleep_awake_bars=True)
    visualize = Visualize(sleep_wake_cycle_plotter=sleep_wake_cycle_plotter)

    # Simulate the sleep data
    sleep_data = model.simulate(ts, sleep_pressure_T0, wake_status_T0)
    visualize.plot_all(sleep_data, ax)
    
    # Add a title to the subplot
    ax.set_title("Default Sleep Behavior")
    
    # Add a legend to the subplot
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper right', fontsize='small')
    plt.show()

def plot_configurations(configurations, model, ts, sleep_pressure_T0, wake_status_T0):
    # Create a figure and subplots
    fig, axs = plt.subplots(2, 3, figsize=(20, 10))
    sleep_wake_cycle_plotter = SleepWakeCyclePlotter(plot_vertical_dashed_lines=True, plot_dots_at_sleep_starts_ends=True, plot_sleep_awake_bars=True)
    visualize = Visualize(sleep_wake_cycle_plotter=sleep_wake_cycle_plotter)

    # Loop over the configurations
    for i, config in enumerate(configurations):
        # Create a new model instance with the merged parameters
        model = BorbelyModel({**default_params, **config})

        # Simulate the sleep data
        sleep_data = model.simulate(ts, sleep_pressure_T0, wake_status_T0)

        # Plot the data in one of the subplots
        ax = axs[i // 3, i % 3]
        visualize.plot_all(sleep_data, ax)

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
    visualize = Visualize()

    # Loop over the configurations
    for i, config in enumerate(configurations):
        # Create a new model instance with the merged parameters
        model = BorbelyModel({**default_params, **config})

        # Simulate the sleep data
        sleep_data = model.simulate(ts, sleep_pressure_T0, wake_status_T0)

        # Plot the sleep-wake bars in one of the subplots
        ax = axs[i]
        visualize.sleep_wake_cycle_plotter.plot_sleep_awake_bars(sleep_data.time, sleep_data.sleep_starts, sleep_data.sleep_ends, ax)

        # Add a title to the subplot
        ax.set_title(config['title'])

    # Adjust the layout and show the figure
    plt.tight_layout()
    plt.show()