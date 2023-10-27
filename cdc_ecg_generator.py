import numpy as np



class CardimetryECGWaveCharacteristics:


    def __init__(self) -> None:

        # Constants
        self.FREQ_CONVERSE  = 0.1047197551

        # Enumerate
        self.P = 0
        self.Q = 1
        self.R = 2
        self.S = 3
        self.T = 4
        
        # Table characteristics
        self.base_amp   = 0.15 
        self.base_freq  = 8.58701992
        self.wave       = [
            {
                'theta' : -np.pi/3.0,
                'a'     : 9.0,
                'b'     : 0.25
            }, 
            {
                'theta' : -np.pi/12.0,
                'a'     : -150.0,
                'b'     : 0.1
            }, 
            {
                'theta' : 0.0,
                'a'     : 900.0,
                'b'     : 0.1
            }, 
            {
                'theta' : np.pi/12.0,
                'a'     : -225,
                'b'     : 0.1
            }, 
            {
                'theta' : np.pi/1.7,
                'a'     : 9.0,
                'b'     : 0.4
            }
        ]

        # Respiratory factor
        self.respiratory_enable = False
        self.respiratory_rate   = 0.23
        self.respiratory_amp    = 0.0

        # RSA factor
        self.rsa_enable     = False
        self.rsa_freq       = 0.25

        # Mayer factor
        self.mayer_enable       = False
        self.mayer_freq         = 0.1
        self.mayer_freq_mov     = 0.01


    def setBaseFrequency(self, bpm:float) -> None:
        self.base_freq = bpm*self.FREQ_CONVERSE

    
    def setBaseAmplitude(self, amp:float) -> None:
        self.base_amp = amp


    def setPWaveCharacteristics(self, theta:float, a:float, b:float) -> None:
        self.p_wave_theta   = theta
        self.p_wave_a       = a
        self.p_wave_b       = b


    def setQWaveCharacteristics(self, theta:float, a:float, b:float) -> None:
        self.q_wave_theta   = theta
        self.q_wave_a       = a
        self.q_wave_b       = b


    def setRWaveCharacteristics(self, theta:float, a:float, b:float) -> None:
        self.r_wave_theta   = theta
        self.r_wave_a       = a
        self.r_wave_b       = b


    def setSWaveCharacteristics(self, theta:float, a:float, b:float) -> None:
        self.s_wave_theta   = theta
        self.s_wave_a       = a
        self.s_wave_b       = b


    def setTWaveCharacteristics(self, theta:float, a:float, b:float) -> None:
        self.t_wave_theta   = theta
        self.t_wave_a       = a
        self.t_wave_b       = b


    def enableRespiratoryFactor(self, amp:float, rate:float=0.23):
        self.respiratory_enable = True
        self.respiratory_rate   = rate
        self.respiratory_amp    = amp


    def disableRespiratoryFactor(self):
        self.respiratory_enable = False


    def enableRSAFactor(self, freq_displacement:float=0.25):
        self.rsa_enable = True
        self.rsa_freq   = freq_displacement


    def disableRSAFactor(self):
        self.rsa_enable = False

    
    def enableMayerFactor(self, freq_displacement:float=0.1, freq_movement:float=0.01):
        self.mayer_enable   = True
        self.mayer_freq     = freq_displacement


    def disableMayerFactor(self):
        self.mayer_enable   = False



class CardimetryECGGenerator:


    def __init__(self, cm_ecg_wave_characteristics) -> None:
        
        # Constants
        self.TIME_STEP = 0.001
        
        # Members
        self.ecg_wave_characteristics = cm_ecg_wave_characteristics
        self.timestamp = 0.0
        self.state = np.array([
            [-1.0],
            [0.0],
            [self.ecg_wave_characteristics.base_amp]
        ])


    def calcAlpha(self, x:np.ndarray) -> float:
        return 1.0 - np.sqrt(x[0].item()**2.0 + x[1].item()**2.0)


    def calcTheta(self, x:np.ndarray) -> float:
        return np.arctan2(x[1].item(), x[0].item())
    

    def calcDiffTheta(self, theta:float, ecg_enum:int) -> float:
        theta_i = self.ecg_wave_characteristics.wave[ecg_enum]['theta']
        return np.fmod(theta - theta_i, 2.0*np.pi)


    def calcZ0(self, time:float) -> float:
        base_amp            = self.ecg_wave_characteristics.base_amp
        respiratory_rate    = self.ecg_wave_characteristics.respiratory_rate
        respiratory_amp     = self.ecg_wave_characteristics.respiratory_amp

        if self.ecg_wave_characteristics.respiratory_enable:
            return base_amp + respiratory_amp*np.sin(2.0*np.pi*respiratory_rate*time)
        
        else:
            return base_amp 
    

    def calcOmega(self, time:float) -> float:
        if self.ecg_wave_characteristics.rsa_enable or self.ecg_wave_characteristics.mayer_enable:
            rsa_fact    = float(self.ecg_wave_characteristics.rsa_enable)*self.ecg_wave_characteristics.rsa_freq*np.sin(2.0*np.pi*self.ecg_wave_characteristics.respiratory_rate*time)
            mayer_fact  = float(self.ecg_wave_characteristics.mayer_enable)*self.ecg_wave_characteristics.mayer_freq*np.sin(2.0*np.pi*self.ecg_wave_characteristics.mayer_freq_mov*time)
            return self.ecg_wave_characteristics.base_freq + rsa_fact + mayer_fact
        else:
            return self.ecg_wave_characteristics.base_freq
        

    def calcSSEquation(self, x:np.ndarray, time:float) -> np.ndarray:
        alpha = self.calcAlpha(x)
        omega = self.calcOmega(time)
        theta = self.calcTheta(x)
        
        z_dot = 0
        for i in range(5):
            a           = self.ecg_wave_characteristics.wave[i]['a']
            b           = self.ecg_wave_characteristics.wave[i]['b']
            dtheta      = self.calcDiffTheta(theta, i)
            exp_term    = np.exp(-(dtheta**2.0)/(2.0*(b**2.0)))
            z_dot       -= a*dtheta*exp_term
        z_dot -= x[2].item() - self.calcZ0(time)

        return np.array([
            [alpha*x[0].item() - omega*x[1].item()],
            [alpha*x[1].item() + omega*x[0].item()],
            [z_dot]
        ])


    def calcNextState(self) -> None:
        self.state      = self.state + self.calcSSEquation(self.state, self.timestamp)*self.TIME_STEP
        # self.state      = self.state + np.array([[0.0], [0.0], [np.random.normal(0.001)]])
        self.timestamp  += self.TIME_STEP
    

    def getCurrentAmp(self) -> float:
        return self.state[2].item() + np.random.normal(loc=0, scale=0.012)
    

    def getCurrentAmpADS1293Format(self) -> int:
        return int((self.state[2].item() + np.random.normal(loc=0, scale=0.012))*15435038.72)
    

    def getCurrentTimeStamp(self) -> float:
        return self.timestamp
    

    def getCurrentTimeStampMillis(self) -> int:
        return int(self.timestamp*1000)