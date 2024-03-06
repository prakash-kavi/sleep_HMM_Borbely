import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class ProcessS:
    # Process S in the Borbely model represents homeostatic sleep pressure that builds up during wakefulness and dissipates during sleep.
    def __init__(self, Sleep_Decay_Rate):
        self.Sleep_Decay_Rate = Sleep_Decay_Rate

    def calculate_sleep_pressure(self, t, H0):
        # Calculate sleep pressure during sleep, decreases exponentially.
        return H0 * np.exp(-t / self.Sleep_Decay_Rate)

class ProcessC:
    # Process C in the Borbely model represents the circadian rhythm, the body's 24-hour sleep-wake cycle.
    def __init__(self, circadian_frequency, circadian_phase_shift, circadian_amplitude, UpperBound_Sleep_Pressure, LowerBound_Sleep_Pressure):
        self.circadian_frequency = circadian_frequency  # w: The angular frequency of the circadian oscillation.
        self.circadian_phase_shift = circadian_phase_shift  # circadian_phase_shift: The phase shift of the circadian oscillation.
        self.circadian_amplitude = circadian_amplitude  # a: The amplitude of the circadian oscillation.
        self.UpperBound_Sleep_Pressure = UpperBound_Sleep_Pressure  # UpperBound_Sleep_Pressure: The baseline level of the upper turning bound.
        self.LowerBound_Sleep_Pressure = LowerBound_Sleep_Pressure  # LowerBound_Sleep_Pressure: The baseline level of the lower turning bound.

    def calculate_circadian_rhythm(self, t):
        # Calculate the circadian oscillation, a sinusoidal function representing the 24-hour sleep-wake cycle.
        return np.sin(self.circadian_frequency * t - self.circadian_phase_shift)

    def calculate_upper_bound(self, t):
        # Calculate the upper bound, the sleep pressure threshold for inducing sleep.
        return self.UpperBound_Sleep_Pressure + self.circadian_amplitude * self.calculate_circadian_rhythm(t)

    def lower(self, t):
        # Calculate the lower bound, the sleep pressure threshold for inducing wakefulness.
        return self.LowerBound_Sleep_Pressure + self.circadian_amplitude * self.calculate_circadian_rhythm(t)

class BorbelyModel:
    # This class represents the Borbely model.
    def __init__(self, parms=None):
        # # Default parameters, based on empirical observations and adjustable for different sleep patterns.
        self.default_parms = {
            'Sleep_Decay_Rate': 4.2,  # Decay rate of sleep pressure during sleep. Higher value leads to slower decay.
            'Wake_Decay_Rate': 18.2,  # Decay rate of sleep pressure during wakefulness. Higher value leads to slower decay.
            'Wake_Baseline_Pressure': 1,  # Baseline sleep pressure during wakefulness. Higher value increases baseline level.
            'circadian_amplitude': 0.1,  # Amplitude of circadian oscillation in sleep pressure. Higher value increases oscillation amplitude.
            'circadian_frequency': 2 * np.pi / 24,  # Frequency of circadian oscillation. Higher value increases oscillation frequency.
            'circadian_phase_shift': 0,  # Phase shift of circadian oscillation. Positive value shifts oscillation to later in the day.
            'UpperBound_Sleep_Pressure': 0.6,  # Baseline of upper bound for sleep pressure. Higher value increases wakefulness threshold.
            'LowerBound_Sleep_Pressure': 0.17  # Baseline of lower bound for sleep pressure. Higher value increases sleep initiation threshold.
        }
        if parms is None:
            self.parms = self.default_parms
        else:
            self.parms = parms

        self.process_s = ProcessS(self.parms['Sleep_Decay_Rate'])
        self.process_c = ProcessC(self.parms['circadian_frequency'], self.parms['circadian_phase_shift'], self.parms['circadian_amplitude'], self.parms['UpperBound_Sleep_Pressure'], self.parms['LowerBound_Sleep_Pressure'])

    def Ha(self, t, H0):
        # Calculate sleep pressure during wakefulness, increases exponentially.
        return self.parms['Wake_Baseline_Pressure'] + (H0 - self.parms['Wake_Baseline_Pressure']) * np.exp(-t / self.parms['Wake_Decay_Rate'])

    def Hc(self, t, H0, awake):
        # Calculate sleep pressure based on wakefulness state.
        return awake * self.Ha(t, H0) + (not awake) * self.process_s.calculate_sleep_pressure(t, H0)

    def simulate(self, ts, sleep_pressure_T0, wake_status_T0=False):
        # Simulate the Borbely model.
        print(f"Wakefulness Threshold: {self.parms['Wake_Baseline_Pressure']}")

        # Get upper and lower bounds
        upper = self.process_c.calculate_upper_bound(ts)
        lower = self.process_c.lower(ts)

        # Initialize sleep pressure and awake state arrays
        H = np.full(len(ts), np.nan)
        awake = np.full(len(ts), np.nan, dtype=bool)
        H[0] = sleep_pressure_T0
        awake[0] = wake_status_T0

        for i in range(1, len(ts)):
            # Calculate sleep pressure
            H[i] = self.Hc(ts[i] - ts[i-1], H[i-1], awake[i-1])
            
            # Check if sleep or wake trigger is activated
            wake_trigger = (not awake[i-1]) and (H[i] <= lower[i])
            sleep_trigger = awake[i-1] and (H[i] >= upper[i])

            # Update awake state based on triggers
            if wake_trigger:
                awake[i] = True
                print(f"Sleep ends at time {ts[i]}")

            elif sleep_trigger:
                awake[i] = False
                print(f"Sleep starts at time {ts[i]}")

            else:
                awake[i] = awake[i-1]

        # Return siWake_Baseline_Pressurelation results
        sol = {'time': ts, 'H': H, 'awake': awake, 'upper': upper, 'lower': lower}
        return sol

class Visualize:
    @staticmethod
    def plot_sleep_periods(ts_days, sleep_starts, sleep_ends, sol):
        for start, end in zip(sleep_starts, sleep_ends):
            plt.plot([ts_days[start]]*2, [0, sol['H'][start]], color='gray', linestyle='--', alpha=0.5)
            plt.plot([ts_days[end]]*2, [0, sol['H'][end]], color='gray', linestyle='--', alpha=0.5)
            plt.plot(ts_days[start], sol['H'][start], 'ro')  # red dot for sleep start
            plt.plot(ts_days[end], sol['H'][end], 'go')  # green dot for sleep end

    @staticmethod
    def plot_sleep_awake_bars(ts_days, sleep_starts, sleep_ends):
        for start, end in zip(sleep_starts, sleep_ends):
            plt.plot([ts_days[start], ts_days[end]], [0, 0], color='red', linewidth=10)

    @staticmethod
    def plot(sol, model):
        ts_days = sol['time']
        plt.plot(ts_days, sol['H'], label='Homeostatic Process - Sleep Pressure')
        plt.plot(ts_days, sol['lower'], label='Circadian Process ')

        sleep_starts = np.where(np.diff(np.sign(sol['H'] - sol['upper'])) == 2)[0]
        sleep_ends = np.where(np.diff(np.sign(sol['H'] - sol['lower'])) == -2)[0]

        Visualize.plot_sleep_periods(ts_days, sleep_starts, sleep_ends, sol)
        Visualize.plot_sleep_awake_bars(ts_days, sleep_starts, sleep_ends)

        red_patch = mpatches.Patch(color='red', label='Sleeping')
        green_patch = mpatches.Patch(color='green', label='Awake')
        plt.legend(handles=[red_patch, green_patch], loc='upper right')

        max_hours = int(np.ceil(sol['time'][-1]))
        tick_locations = np.arange(0, max_hours + 1, 24)
        plt.xticks(tick_locations)

        plt.xlim(left=0)
        plt.ylim(bottom=0)

        plt.title("Borbely - Process S and Process C")
        plt.xlabel('Time (h)')
        plt.ylabel('Sleep Pressure')
        plt.legend()
        plt.show()

ts = np.linspace(0, 72, num=1000)
model = BorbelyModel()
sleep_pressure_T0 = model.parms['Wake_Baseline_Pressure']
wake_status_T0 = False
sol = model.simulate(ts, sleep_pressure_T0, wake_status_T0)
Visualize.plot(sol, model)