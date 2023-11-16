import sys
import cdc_ecg_generator as cdc_ecg
import cdc_imu_generator as cdc_imu
import paho.mqtt.client as mqtt
import requests
import threading
import time
import datetime
import numpy as np


# Global shared variables
cdc_ecg_task_ok     = True
cdc_imu_task_ok     = True
cdc_mqtt_task_ok    = True
cdc_ecg_task_lock   = threading.Lock()
cdc_imu_task_lock   = threading.Lock()
cdc_mqtt_task_lock  = threading.Lock()

ECG_QUEUE_SIZE      = 100
ecg_ts_q1           = ""
ecg_lead1_q1        = ""
ecg_lead2_q1        = ""
ecg_lead3_q1        = ""
ecg_ts_q2           = ""
ecg_lead1_q2        = ""
ecg_lead2_q2        = ""
ecg_lead3_q2        = ""
ecg_permit_to_send  = 0
ecg_lock            = threading.Lock()

IMU_QUEUE_SIZE      = 50
imu_ts_q1           = ""
imu_qw_q1           = ""
imu_qx_q1           = ""
imu_qy_q1           = ""
imu_qz_q1           = ""
imu_ts_q2           = ""
imu_qw_q2           = ""
imu_qx_q2           = ""
imu_qy_q2           = ""
imu_qz_q2           = ""
imu_permit_to_send  = 0
imu_lock            = threading.Lock()




def cdc_ecg_task(task_lock, ecg_lock):

    # Global variables
    global cdc_ecg_task_ok
    global ecg_ts_q1
    global ecg_lead1_q1
    global ecg_lead2_q1
    global ecg_lead3_q1
    global ecg_ts_q2
    global ecg_lead1_q2
    global ecg_lead2_q2
    global ecg_lead3_q2
    global ecg_permit_to_send

    # Local variables
    SAMPLING_RELATIVE_COUNT = 10
    sampling_cnt            = 0
    queue_select            = 1
    queue_cnt               = 0

    # Create and modify the ECG wave characteristics
    random_val = np.random.rand()

    cm_ecg_lead1 = cdc_ecg.CardimetryECGWaveCharacteristics()
    if str(sys.argv[3]) == 'a':
        cm_ecg_lead1.setBaseAmplitude(0.7)
        cm_ecg_lead1.setBaseFrequency(70 + random_val*50)
        cm_ecg_lead1.enableRespiratoryFactor(0.005 + random_val*0.01, 0.24)
        cm_ecg_lead1.enableRSAFactor(0.1)
        cm_ecg_lead1.enableMayerFactor()
    else:
        cm_ecg_lead1.setBaseAmplitude(0.3)
        cm_ecg_lead1.setBaseFrequency(70 + random_val*30)

    cm_ecg_lead2 = cdc_ecg.CardimetryECGWaveCharacteristics()
    if str(sys.argv[3]) == 'a':
        cm_ecg_lead2.setBaseAmplitude(0.4)
        cm_ecg_lead2.setBaseFrequency(70 + random_val*50)
        cm_ecg_lead2.enableRespiratoryFactor(0.005 + random_val*0.01, 0.24)
        cm_ecg_lead2.enableRSAFactor(0.1)
        cm_ecg_lead2.enableMayerFactor()
        cm_ecg_lead2.setRWaveCharacteristics(500, 0.1)
    else:
        cm_ecg_lead2.setBaseAmplitude(0.13)
        cm_ecg_lead2.setBaseFrequency(70 + random_val*30)
        cm_ecg_lead2.setRWaveCharacteristics(500, 0.1)

    # Create an ECG generator
    cm_ecg_generator_lead1 = cdc_ecg.CardimetryECGGenerator(cm_ecg_lead1)
    cm_ecg_generator_lead2 = cdc_ecg.CardimetryECGGenerator(cm_ecg_lead2)

    # Loop
    task_run = True
    while task_run:

        # Generator run
        cm_ecg_generator_lead1.calcNextState()
        cm_ecg_generator_lead2.calcNextState()


        # Increment count, checks whether the sampling can be done
        sampling_cnt = (sampling_cnt + 1)%SAMPLING_RELATIVE_COUNT
        if sampling_cnt == 0:

            ts      = time.time()*1000
            lead1   = cm_ecg_generator_lead1.getCurrentAmpADS1293Format()
            lead2   = cm_ecg_generator_lead1.getCurrentAmpADS1293Format()
            lead3   = lead1 - lead2

            if queue_select == 1:
                ecg_ts_q1    += str(ts) + ','
                ecg_lead1_q1 += str(lead1) + ','
                ecg_lead2_q1 += str(lead2) + ','
                ecg_lead3_q1 += str(lead3) + ','

            elif queue_select == 2:
                ecg_ts_q2    += str(ts) + ','
                ecg_lead1_q2 += str(lead1) + ','
                ecg_lead2_q2 += str(lead2) + ','
                ecg_lead3_q2 += str(lead3) + ','

            queue_cnt += 1


        # If queue is full, permit to publish
        if queue_cnt == ECG_QUEUE_SIZE:

            if queue_select == 1:
                with ecg_lock:
                    ecg_permit_to_send = 1

            elif queue_select == 2:
                with ecg_lock:
                    ecg_permit_to_send = 2

            # Reset and switch
            queue_cnt       = 0
            queue_select    = (queue_select)%2 + 1


        # Retrieve running status
        with task_lock:
            task_run = cdc_ecg_task_ok

        
        # Delay 1ms because the generator works that way
        time.sleep(0.001)


    # Notify if the task ended
    print("ECG task terminated")




def cdc_imu_task(task_lock, imu_lock):
    
    # Global variables
    global cdc_imu_task_ok
    global imu_ts_q1
    global imu_qw_q1
    global imu_qx_q1
    global imu_qy_q1
    global imu_qz_q1
    global imu_ts_q2
    global imu_qw_q2
    global imu_qx_q2
    global imu_qy_q2
    global imu_qz_q2
    global imu_permit_to_send

    # Local variables
    queue_select    = 1
    queue_cnt       = 0

    # Create IMU generator
    cm_imu_generator = cdc_imu.CardimetryIMUGenerator()

    # Loop
    task_run = True
    while task_run:

        # Generator next step
        cm_imu_generator.stepOrientation()


        # Store data to queue
        if queue_select == 1:
            imu_ts_q1   += str(time.time()*1000) + ','
            imu_qw_q1   += str(cm_imu_generator.getOrientationQw()) + ','
            imu_qx_q1   += str(cm_imu_generator.getOrientationQx()) + ','
            imu_qy_q1   += str(cm_imu_generator.getOrientationQy()) + ','
            imu_qz_q1   += str(cm_imu_generator.getOrientationQz()) + ','

        elif queue_select == 2:
            imu_ts_q2   += str(time.time()*1000) + ','
            imu_qw_q2   += str(cm_imu_generator.getOrientationQw()) + ','
            imu_qx_q2   += str(cm_imu_generator.getOrientationQx()) + ','
            imu_qy_q2   += str(cm_imu_generator.getOrientationQy()) + ','
            imu_qz_q2   += str(cm_imu_generator.getOrientationQz()) + ','

        queue_cnt += 1


        # If queue is full, permit to publish
        if queue_cnt == IMU_QUEUE_SIZE:

            if queue_select == 1:
                with imu_lock:
                    imu_permit_to_send = 1

            elif queue_select == 2:
                with imu_lock:
                    imu_permit_to_send = 2

            # Reset and switch
            queue_cnt       = 0
            queue_select    = (queue_select)%2 + 1


        # Retrieve running status
        with task_lock:
            task_run = cdc_imu_task_ok


        # Delay as generator expected
        time.sleep(0.02)

    
    # Notify if the task ended
    print("IMU task terminated")




def cdc_mqtt_task(task_lock, ecg_lock, imu_lock):

    # Global variables
    global cdc_mqtt_task_ok
    global ecg_ts_q1
    global ecg_lead1_q1
    global ecg_lead2_q1
    global ecg_lead3_q1
    global ecg_ts_q2
    global ecg_lead1_q2
    global ecg_lead2_q2
    global ecg_lead3_q2
    global ecg_permit_to_send
    global imu_ts_q1
    global imu_qw_q1
    global imu_qx_q1
    global imu_qy_q1
    global imu_qz_q1
    global imu_ts_q2
    global imu_qw_q2
    global imu_qx_q2
    global imu_qy_q2
    global imu_qz_q2
    global imu_permit_to_send
    
    # Local variable
    CLIENT_NAME     = str(sys.argv[1])
    PATIENT_NAME    = str(sys.argv[2])
    SERVER_ADDRESS  = "192.168.0.214"
    MQTT_PORT       = 1883
    TIME_TOPIC      = f"/time/{CLIENT_NAME}/{PATIENT_NAME}"
    ECG_TOPIC       = f"/ecg/{CLIENT_NAME}/{PATIENT_NAME}"
    IMU_TOPIC       = f"/imu/{CLIENT_NAME}/{PATIENT_NAME}"
    ecg_permit      = 0
    imu_permit      = 0
    ecg_cmml        = ""
    imu_cmml        = ""

    # Request to register
    # response = requests.post(f"https://{SERVER_ADDRESS}/api/v1/device/{CLIENT_NAME}")
    # response = requests.post(f"https://{SERVER_ADDRESS}/api/v1/device/{CLIENT_NAME}/{PATIENT_NAME}")

    # Start MQTT
    client = mqtt.Client(CLIENT_NAME)
    client.connect(SERVER_ADDRESS, MQTT_PORT)

    # Send initiate
    client.publish(TIME_TOPIC, str(time.mktime(datetime.datetime.now().timetuple())))

    # Loop
    task_run = True
    while task_run:

        # Retrieve ecg and imu permission
        with ecg_lock:
            ecg_permit = ecg_permit_to_send
        with imu_lock:
            imu_permit = imu_permit_to_send

        
        # Case division
        if ecg_permit == 1:

            # Transmit data and reset
            ecg_cmml        = '$' + ecg_ts_q1 + '$' + ecg_lead1_q1 + '$' + ecg_lead2_q1 + '$' + ecg_lead3_q1
            ecg_ts_q1       = ""
            ecg_lead1_q1    = ""
            ecg_lead2_q1    = ""
            ecg_lead3_q1    = ""
            # print('-------------[ ECG QUEUE 1 ]-------------')
            # print(ecg_cmml)
            client.publish(ECG_TOPIC, ecg_cmml)

            # Reset
            ecg_permit = 0
            with ecg_lock:
                ecg_permit_to_send = 0


        elif ecg_permit == 2:

            # Transmit data and reset
            ecg_cmml        = '$' + ecg_ts_q2 + '$' + ecg_lead1_q2 + '$' + ecg_lead2_q2 + '$' + ecg_lead3_q2
            ecg_ts_q2       = ""
            ecg_lead1_q2    = ""
            ecg_lead2_q2    = ""
            ecg_lead3_q2    = ""
            # print('-------------[ ECG QUEUE 2 ]-------------')
            # print(ecg_cmml)
            client.publish(ECG_TOPIC, ecg_cmml)

            # Reset
            ecg_permit = 0
            with ecg_lock:
                ecg_permit_to_send = 0

        
        if imu_permit == 1:
            
            # Transmit data and reset
            imu_cmml    = '$' + imu_ts_q1 + '$' + imu_qw_q1 + '$' + imu_qx_q1 + '$' + imu_qy_q1 + '$' + imu_qz_q1
            imu_ts_q1   = ""
            imu_qw_q1   = ""
            imu_qx_q1   = ""
            imu_qy_q1   = ""
            imu_qz_q1   = ""
            # print('-------------[ IMU QUEUE 1 ]-------------')
            # print(imu_cmml)
            client.publish(IMU_TOPIC, imu_cmml)

            # Reset
            imu_permit = 0
            with imu_lock:
                imu_permit_to_send = 0


        elif imu_permit == 2:
            
            # Transmit data and reset
            imu_cmml    = '$' + imu_ts_q2 + '$' + imu_qw_q2 + '$' + imu_qx_q2 + '$' + imu_qy_q2 + '$' + imu_qz_q2
            imu_ts_q2   = ""
            imu_qw_q2   = ""
            imu_qx_q2   = ""
            imu_qy_q2   = ""
            imu_qz_q2   = ""
            # print('-------------[ IMU QUEUE 2 ]-------------')
            # print(imu_cmml)
            client.publish(IMU_TOPIC, imu_cmml)

            # Reset
            imu_permit = 0
            with imu_lock:
                imu_permit_to_send = 0


        # Retrieve running status
        with task_lock:
            task_run = cdc_mqtt_task_ok


        # Delay for 300ms because why not
        time.sleep(0.3)

    
    # Notify if the task ended
    client.disconnect()
    print("MQTT task terminated")




def cdc_control_task(ecg_task_lock, imu_task_lock, mqtt_task_lock):

    # Global variables
    global cdc_ecg_task_ok
    global cdc_imu_task_ok
    global cdc_mqtt_task_ok

    # Local variable
    task_run = True

    # Loop
    while task_run:
        key = input("Insert Q to quit: ")
        
        if key == 'Q':
            with ecg_task_lock:
                cdc_ecg_task_ok = False
            with imu_task_lock:
                cdc_imu_task_ok = False
            with mqtt_task_lock:
                cdc_mqtt_task_ok = False
            
            task_run = False

    # Notify
    print('Terminating tasks...')




# Start tasks
cdc_ecg_thread = threading.Thread(
    target  = cdc_ecg_task, 
    args    = (cdc_ecg_task_lock, ecg_lock)
)
cdc_imu_thread = threading.Thread(
    target  = cdc_imu_task,
    args    = (cdc_imu_task_lock, imu_lock)
)
cdc_mqtt_thread = threading.Thread(
    target  = cdc_mqtt_task, 
    args    = (cdc_mqtt_task_lock, ecg_lock, imu_lock)
)
cdc_control_thread = threading.Thread(
    target  = cdc_control_task,
    args    = (cdc_ecg_task_lock, cdc_imu_task_lock, cdc_mqtt_task_lock)
)

cdc_ecg_thread.start()
cdc_imu_thread.start()
cdc_mqtt_thread.start()
cdc_control_thread.start()

cdc_ecg_thread.join()
cdc_imu_thread.join()
cdc_mqtt_thread.join()
cdc_control_thread.join()