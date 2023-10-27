import submodules.cdc_ecg_generator as cdc_ecg
import submodules.cdc_mqtt_client as cdc_mqtt
import matplotlib.pyplot as plt

# Modify the ECG wave characteristics
cm_ecg_wave = cdc_ecg.CardimetryECGWaveCharacteristics()

# Create an ECG generator
cm_ecg_generator = cdc_ecg.CardimetryECGGenerator(cm_ecg_wave)




# # Initiate
# state_history   = [cm_ecg_generator.getCurrentAmp()]
# time_stamp      = [cm_ecg_generator.getCurrentTimeStamp()]

# # Loop
# SAMPLING_COUNT = 10
# sampling_cnt = 0
# for i in range(20000):
#     cm_ecg_generator.calcNextState()
#     sampling_cnt = (sampling_cnt + 1)%SAMPLING_COUNT
#     if sampling_cnt == 0:
#         state_history.append(cm_ecg_generator.getCurrentAmp())
#         time_stamp.append(cm_ecg_generator.getCurrentTimeStamp())


# plt.plot(time_stamp, state_history)
# plt.show()