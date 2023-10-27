import cdc_ecg_generator as cdc_ecg
import paho.mqtt.client as mqtt
import threading
import time


# Global shared variables
cdc_ecg_task_ok     = True
cdc_mqtt_task_ok    = True
cdc_ecg_task_lock   = threading.Lock()
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
    cm_ecg_lead1 = cdc_ecg.CardimetryECGWaveCharacteristics()
    cm_ecg_lead2 = cdc_ecg.CardimetryECGWaveCharacteristics()
    cm_ecg_lead3 = cdc_ecg.CardimetryECGWaveCharacteristics()

    # Create an ECG generator
    cm_ecg_generator_lead1 = cdc_ecg.CardimetryECGGenerator(cm_ecg_lead1)
    cm_ecg_generator_lead2 = cdc_ecg.CardimetryECGGenerator(cm_ecg_lead2)
    cm_ecg_generator_lead3 = cdc_ecg.CardimetryECGGenerator(cm_ecg_lead3)

    # Loop
    task_run = True
    while task_run:

        # Generator run
        cm_ecg_generator_lead1.calcNextState()
        cm_ecg_generator_lead2.calcNextState()
        cm_ecg_generator_lead3.calcNextState()


        # Increment count, checks whether the sampling can be done
        sampling_cnt = (sampling_cnt + 1)%SAMPLING_RELATIVE_COUNT
        if sampling_cnt == 0:

            if queue_select == 1:
                ecg_ts_q1    += str(cm_ecg_generator_lead1.getCurrentTimeStampMillis()) + ','
                ecg_lead1_q1 += str(cm_ecg_generator_lead1.getCurrentAmpADS1293Format()) + ','
                ecg_lead2_q1 += str(cm_ecg_generator_lead2.getCurrentAmpADS1293Format()) + ','
                ecg_lead3_q1 += str(cm_ecg_generator_lead3.getCurrentAmpADS1293Format()) + ','

            elif queue_select == 2:
                ecg_ts_q2    += str(cm_ecg_generator_lead1.getCurrentTimeStampMillis()) + ','
                ecg_lead1_q2 += str(cm_ecg_generator_lead1.getCurrentAmpADS1293Format()) + ','
                ecg_lead2_q2 += str(cm_ecg_generator_lead2.getCurrentAmpADS1293Format()) + ','
                ecg_lead3_q2 += str(cm_ecg_generator_lead3.getCurrentAmpADS1293Format()) + ','

            queue_cnt += 1


        # If queue is full, permit to publish
        if queue_cnt == ECG_QUEUE_SIZE:

            if queue_select == 1:
                # print('[QUEUE 1]')
                # print(ecg_lead1_q1)
                with ecg_lock:
                    ecg_permit_to_send = 1

            elif queue_select == 2:
                # print('[QUEUE 2]')
                # print(ecg_lead1_q2)
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
    print("ECG Task ended")




def cdc_mqtt_task(task_lock, ecg_lock):

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
    
    # Local variable
    CLIENT_NAME     = "CMdummy01"
    BROKER_ADDRESS  = "192.168.1.100"
    BROKER_PORT     = 1883
    ECG_TOPIC       = f"/{CLIENT_NAME}/ecg/pub"
    IMU_TOPIC       = f"/{CLIENT_NAME}/imu/pub"
    ecg_permit      = 0
    imu_permit      = 0
    ecg_cmml        = ""

    # Start MQTT
    client = mqtt.Client(CLIENT_NAME)
    client.connect(BROKER_ADDRESS, BROKER_PORT)

    # Loop
    task_run = True
    while task_run:

        # Retrieve ecg permission
        with ecg_lock:
            ecg_permit = ecg_permit_to_send

        
        # Case division
        if ecg_permit == 1:

            # Transmit data and reset
            ecg_cmml        = '$' + ecg_ts_q1 + '$' + ecg_lead1_q1 + '$' + ecg_lead2_q1 + '$' + ecg_lead3_q1
            ecg_ts_q1       = ""
            ecg_lead1_q1    = ""
            ecg_lead2_q1    = ""
            ecg_lead3_q1    = ""
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
            client.publish(ECG_TOPIC, ecg_cmml)

            # Reset
            ecg_permit = 0
            with ecg_lock:
                ecg_permit_to_send = 0


        # Retrieve running status
        with task_lock:
            task_run = cdc_mqtt_task_ok


        # Delay for 400ms because why not
        time.sleep(0.4)

    
    # Notify if the task ended
    client.disconnect()
    print("MQTT Task ended")




def cdc_control_task(ecg_task_lock, mqtt_task_lock):

    # Global variables
    global cdc_ecg_task_ok
    global cdc_mqtt_task_ok

    # Local variable
    task_run = True

    # Loop
    while task_run:
        key = input("Insert Q to quit: ")
        
        if key == 'Q':
            with ecg_task_lock:
                cdc_ecg_task_ok = False
            with mqtt_task_lock:
                cdc_mqtt_task_ok = False
            
            task_run = False




# Start tasks
cdc_ecg_thread = threading.Thread(
    target  = cdc_ecg_task, 
    args    = (cdc_ecg_task_lock, ecg_lock)
)
cdc_mqtt_thread = threading.Thread(
    target  = cdc_mqtt_task, 
    args    = (cdc_mqtt_task_lock, ecg_lock)
)
cdc_control_thread = threading.Thread(
    target  = cdc_control_task,
    args    = (cdc_ecg_task_lock, cdc_mqtt_task_lock)
)

cdc_ecg_thread.start()
cdc_mqtt_thread.start()
cdc_control_thread.start()

cdc_ecg_thread.join()
cdc_mqtt_thread.join()
cdc_control_thread.join()