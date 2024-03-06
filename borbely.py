import numpy as np
import matplotlib.pyplot as plt

from config import default_params

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
        return self.circadian_amplitude * np.sin(self.circadian_frequency * t - self.circadian_phase_shift)

    def calculate_upper_bound(self, t):
        # Calculate the upper bound, the sleep pressure threshold for inducing sleep.
        return self.UpperBound_Sleep_Pressure + self.circadian_amplitude * self.calculate_circadian_rhythm(t)

    def calculate_lower_bound(self, t):
        # Calculate the lower bound, the sleep pressure threshold for inducing wakefulness.
        return self.LowerBound_Sleep_Pressure + self.circadian_amplitude * self.calculate_circadian_rhythm(t)

class BorbelyModel:
    # This class represents the Borbely model.
    def __init__(self, params=None):
        if params is None:
            self.params = default_params
        else:
            self.params = params

        self.process_s = ProcessS(self.params['Sleep_Decay_Rate'])
        self.process_c = ProcessC(self.params['circadian_frequency'], self.params['circadian_phase_shift'], self.params['circadian_amplitude'], self.params['UpperBound_Sleep_Pressure'], self.params['LowerBound_Sleep_Pressure'])

    def Ha(self, t, H0):
        # Calculate sleep pressure during wakefulness, increases exponentially.
        return self.params['Wake_Baseline_Pressure'] + (H0 - self.params['Wake_Baseline_Pressure']) * np.exp(-t / self.params['Wake_Decay_Rate'])

    def Hc(self, t, H0, awake):
        # Calculate sleep pressure based on wakefulness state.
        return awake * self.Ha(t, H0) + (not awake) * self.process_s.calculate_sleep_pressure(t, H0)

    def calculate_sleep_pressure(self, ts, H0, awake):
        # Calculate sleep pressure based on wakefulness state.
        H = np.full(len(ts), np.nan)
        H[0] = H0 / self.params['Max_Sleep_Pressure']

        for i in range(1, len(ts)):
            H[i] = awake[i-1] * self.Ha(ts[i] - ts[i-1], H[i-1]) + (not awake[i-1]) * self.process_s.calculate_sleep_pressure(ts[i] - ts[i-1], H[i-1])
            H[i] /= self.params['Max_Sleep_Pressure']

        return H

    def determine_sleep_wake_state(self, ts, H, upper, lower, wake_status_T0):
        # Determine sleep/wake state based on sleep pressure and upper/lower bounds.
        awake = np.full(len(ts), np.nan, dtype=bool)
        awake[0] = wake_status_T0

        sleep_starts = []
        sleep_ends = []

        for i in range(1, len(ts)):
            if awake[i-1] and H[i] >= upper[i]:
                awake[i] = False
                if i < len(ts) - 1:
                    sleep_starts.append(ts[i])
            elif (not awake[i-1]) and H[i] <= lower[i]:
                awake[i] = True
                if i < len(ts) - 1:
                    sleep_ends.append(ts[i])
            else:
                awake[i] = awake[i-1]

        return awake, sleep_starts, sleep_ends

    def simulate(self, ts, sleep_pressure_T0, wake_status_T0=False):
        # Simulate the Borbely model.
        print(f"Wakefulness Threshold: {self.params['Wake_Baseline_Pressure']}")

        # Get upper and lower bounds
        upper = self.process_c.calculate_upper_bound(ts)
        lower = self.process_c.calculate_lower_bound(ts)

        # Initialize arrays
        H = np.full(len(ts), np.nan)
        H[0] = sleep_pressure_T0
        awake = np.full(len(ts), wake_status_T0, dtype=bool)

        sleep_starts = []
        sleep_ends = []

        # Calculate sleep pressure and determine sleep/wake state
        for i in range(1, len(ts)):
            dt = ts[i] - ts[i-1]
            H[i] = awake[i-1] * self.Ha(dt, H[i-1]) + (not awake[i-1]) * self.process_s.calculate_sleep_pressure(dt, H[i-1])

            if awake[i-1] and H[i] >= upper[i]:
                awake[i] = False
                sleep_starts.append(ts[i])
            elif (not awake[i-1]) and H[i] <= lower[i]:
                awake[i] = True
                sleep_ends.append(ts[i])
            else:
                awake[i] = awake[i-1]

        # Add the end of the simulation as the end time of the last sleep period if necessary
        if len(sleep_starts) > len(sleep_ends):
            sleep_ends.append(ts[-1])
            
        # Return simulation results as an instance of SleepData
        sleep_data = SleepData(ts, H, awake, upper, lower, sleep_starts, sleep_ends, self.process_c.calculate_circadian_rhythm)        
        sleep_data.identify_sleep_periods()  # Print the sleep periods by index
        return sleep_data
    
class SleepData:
    # This class encapsulates the sleep data and provides methods for accessing it.
    def __init__(self, time, H, awake, calculate_upper_bound, calculate_lower_bound, sleep_starts, sleep_ends, calculate_circadian_rhythm):
        self.time = time
        self.H = H
        self.awake = awake
        self.upper = calculate_upper_bound
        self.lower = calculate_lower_bound
        self.sleep_starts = sleep_starts
        self.sleep_ends = sleep_ends
        self.calculate_circadian_rhythm = calculate_circadian_rhythm  # Add a reference to the calculate_circadian_rhythm function


    def identify_sleep_periods(self):
        # Identifies the sleep periods.
        sleep_starts = []
        sleep_ends = []
        first_wake = False
        for i in range(1, len(self.time)):
            if not first_wake and self.awake[i]:
                first_wake = True
            if first_wake:
                if self.awake[i-1] and not self.awake[i]:
                    sleep_starts.append(self.time[i])
                elif not self.awake[i-1] and self.awake[i]:
                    sleep_ends.append(self.time[i])
        sleep_periods = list(zip(sleep_starts, sleep_ends))
        for i, (start, end) in enumerate(sleep_periods):
            print(f"Sleep period {i+1}: starts at {start}, ends at {end}")
        return sleep_starts, sleep_ends
    