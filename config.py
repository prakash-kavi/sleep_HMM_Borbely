import numpy as np

configurations = [
    {
        'simulation_key': 'default',
        'circadian_amplitude': 0.2,
        'circadian_phase_shift': 0,
        'title': 'Default Condition'
    },
    {
        'simulation_key': 'light_exposure',
        'circadian_amplitude': 0.2,
        'circadian_phase_shift': 2,
        'title': 'Light Exposure'
    },
    {
        'simulation_key': 'age',
        'circadian_amplitude': 0.1,
        'circadian_phase_shift': -2,
        'title': 'Age'
    },
    {
        'simulation_key': 'jet_lag',
        'circadian_amplitude': 0.15,
        'circadian_phase_shift': 4,
        'title': 'Time Zone Changes'
    },
    {
        'simulation_key': 'shift_work',
        'circadian_amplitude': 0.15,
        'circadian_phase_shift': -4,
        'title': 'Shift Work'
    },
    {
        'simulation_key': 'sleep_deprived',
        'circadian_amplitude': 0.4,
        'circadian_phase_shift': 0,
        'title': 'Sleep Deprivation'
    }
]

default_params = {
    'Sleep_Decay_Rate': 4.2,
    'Wake_Decay_Rate': 18.2,
    'Wake_Baseline_Pressure': 1,
    'circadian_amplitude': 0.3,
    'circadian_frequency': 2 * np.pi / 24,
    'circadian_phase_shift': 0,
    'UpperBound_Sleep_Pressure': 0.6,
    'LowerBound_Sleep_Pressure': 0.17,
    'Max_Sleep_Pressure': 1  # Maximum possible value of sleep pressure
}