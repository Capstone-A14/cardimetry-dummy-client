import numpy as np
import pandas as pd



class CardimetryIMUGenerator:


    def __init__(self) -> None:
        
        # Constants
        self.TRANSITION_STEP    = 10
        self.TIME_STEP          = 0.02
        self.DATASET_NUM        = 15

        # Members
        self.timestamp          = 0.0
        self.counter            = 0
        self.data_cursor        = np.random.randint(0, self.DATASET_NUM)
        self.last_cursor        = 0
        self.transition         = False
        self.transition_counter = 1

        # Read CSV with pandas
        self.imu_df = [
            pd.read_csv('imu_dataset/P01_PELVIS.csv'),
            pd.read_csv('imu_dataset/P02_PELVIS.csv'),
            pd.read_csv('imu_dataset/P03_PELVIS.csv'),
            pd.read_csv('imu_dataset/P04_PELVIS.csv'),
            pd.read_csv('imu_dataset/P05_PELVIS.csv'),
            pd.read_csv('imu_dataset/P06_PELVIS.csv'),
            pd.read_csv('imu_dataset/P07_PELVIS.csv'),
            pd.read_csv('imu_dataset/P08_PELVIS.csv'),
            pd.read_csv('imu_dataset/P09_PELVIS.csv'),
            pd.read_csv('imu_dataset/P10_PELVIS.csv'),
            pd.read_csv('imu_dataset/P11_PELVIS.csv'),
            pd.read_csv('imu_dataset/P12_PELVIS.csv'),
            pd.read_csv('imu_dataset/P13_PELVIS.csv'),
            pd.read_csv('imu_dataset/P14_PELVIS.csv'),
            pd.read_csv('imu_dataset/P15_PELVIS.csv')
        ]
        self.imu_df_len = [
            len(self.imu_df[0]),
            len(self.imu_df[1]),
            len(self.imu_df[2]),
            len(self.imu_df[3]),
            len(self.imu_df[4]),
            len(self.imu_df[5]),
            len(self.imu_df[6]),
            len(self.imu_df[7]),
            len(self.imu_df[8]),
            len(self.imu_df[9]),
            len(self.imu_df[10]),
            len(self.imu_df[11]),
            len(self.imu_df[12]),
            len(self.imu_df[13]),
            len(self.imu_df[14]),
        ]
        self.orientation = np.array([
            [self.imu_df[self.data_cursor]['q0'][0]],
            [self.imu_df[self.data_cursor]['q1'][0]],
            [self.imu_df[self.data_cursor]['q2'][0]],
            [self.imu_df[self.data_cursor]['q3'][0]]
        ])


    def stepOrientation(self) -> None:

        # Update time
        self.timestamp += self.TIME_STEP


        # Update orientation
        if not self.transition:
            self.counter += 1

        else:
            self.transition_counter += 1

        
        # Update cursor if maximum length achieved
        if self.counter == self.imu_df_len[self.data_cursor]:
            
            # Transition
            self.transition     = True
            self.last_cursor    = self.data_cursor
            self.data_cursor    = np.random.randint(0, self.DATASET_NUM)

            # Reset
            self.counter = 0

        elif self.transition_counter == self.TRANSITION_STEP:
            
            # Stop transition
            self.transition = False

            # Reset
            self.transition_counter = 1
        

        # Check whether it is transition or not
        if self.transition:
            self.orientation = [
                [((float(self.transition_counter))/10.)*self.imu_df[self.data_cursor]['q0'][0] + ((10. - float(self.transition_counter))/10.)*self.imu_df[self.last_cursor]['q0'][self.imu_df_len[self.last_cursor]-1]],
                [((float(self.transition_counter))/10.)*self.imu_df[self.data_cursor]['q1'][0] + ((10. - float(self.transition_counter))/10.)*self.imu_df[self.last_cursor]['q1'][self.imu_df_len[self.last_cursor]-1]],
                [((float(self.transition_counter))/10.)*self.imu_df[self.data_cursor]['q2'][0] + ((10. - float(self.transition_counter))/10.)*self.imu_df[self.last_cursor]['q2'][self.imu_df_len[self.last_cursor]-1]],
                [((float(self.transition_counter))/10.)*self.imu_df[self.data_cursor]['q3'][0] + ((10. - float(self.transition_counter))/10.)*self.imu_df[self.last_cursor]['q3'][self.imu_df_len[self.last_cursor]-1]]
            ]
            self.orientation = self.orientation/np.linalg.norm(self.orientation)
        
        else:
            self.orientation = np.array([
                [self.imu_df[self.data_cursor]['q0'][self.counter]],
                [self.imu_df[self.data_cursor]['q1'][self.counter]],
                [self.imu_df[self.data_cursor]['q2'][self.counter]],
                [self.imu_df[self.data_cursor]['q3'][self.counter]]
            ])


    def getTimeStamp(self) -> float:
        return self.timestamp
    

    def getTimeStampMillis(self) -> int:
        return int(self.timestamp*1000)


    def getOrientationQw(self) -> float:
        return self.orientation[0].item()
    

    def getOrientationQx(self) -> float:
        return self.orientation[1].item()
    

    def getOrientationQy(self) -> float:
        return self.orientation[2].item()
    

    def getOrientationQz(self) -> float:
        return self.orientation[3].item()