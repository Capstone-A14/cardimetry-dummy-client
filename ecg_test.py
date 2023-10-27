import cdc_ecg_generator as cdc_ecg
import numpy as np
import matplotlib.pyplot as plt


# Parameters
SIMULATION_TIME = 3000  # in ms
SAMPLING_DIV    = 10    # the value represents period of sampling in ms


# ECG generator
ecg_wave = cdc_ecg.CardimetryECGWaveCharacteristics()
# ecg_wave.setBaseFrequency(120)
# ecg_wave.enableRespiratoryFactor(0.01, 0.4)
# ecg_wave.enableRSAFactor(5)
# ecg_wave.enableMayerFactor()
ecg_generator = cdc_ecg.CardimetryECGGenerator(ecg_wave)


# Simulation Loop
time_stamp      = [ecg_generator.getCurrentTimeStamp()]
ecg_amplitude   = [ecg_generator.getCurrentAmp()]
sampling_cnt    = 0

for t in range(SIMULATION_TIME):

    # Step update
    ecg_generator.calcNextState()

    # Sampling count
    sampling_cnt = (sampling_cnt + 1) % SAMPLING_DIV
    if sampling_cnt == 0:
        time_stamp.append(ecg_generator.getCurrentTimeStamp())
        ecg_amplitude.append(ecg_generator.getCurrentAmp())


# Plot
plt.plot(time_stamp, ecg_amplitude)
plt.show()