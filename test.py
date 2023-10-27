import numpy as np
import matplotlib.pyplot as plt



A_FACT = 30
B_FACT = 1

wave_chr = [
    {
        'theta': -np.pi/3.0,
        'a': 0.3*A_FACT,
        'b': 0.25*B_FACT
    },
    {
        'theta': -np.pi/12.0,
        'a': -5.0*A_FACT,
        'b': 0.1*B_FACT
    },
    {
        'theta': 0,
        'a': 30.0*A_FACT,
        'b': 0.1*B_FACT
    },
    {
        'theta': np.pi/12,
        'a': -7.5*A_FACT,
        'b': 0.1*B_FACT
    },
    {
        'theta': np.pi/1.7,
        'a': 0.3*A_FACT,
        'b': 0.4*B_FACT
    }
]



def ecgSSEq(x:np.ndarray, time:float) -> np.ndarray:
    alpha = 1.0 - np.sqrt(x[0].item()**2.0 + x[1].item()**2.0)
    omega = 8.5

    z_dot = 0
    for i in range(len(wave_chr)):
        a           = wave_chr[i]['a']
        b           = wave_chr[i]['b']
        theta       = np.arctan2(x[1].item(), x[0].item())
        theta_diff  = np.fmod(theta - wave_chr[i]['theta'], 2.0*np.pi)
        exp_term    = np.exp(-((theta_diff)**2.0)/(2.0*(b**2.0)))
        z_dot       -= a*theta_diff*exp_term

    z_dot -= x[2].item() - 0.15 + 0.01*np.sin(2*np.pi*0.24*time)

    return np.array([
        [alpha*x[0].item() - omega*x[1].item()],
        [alpha*x[1].item() + omega*x[0].item()],
        [z_dot]
    ])



state = np.array([
    [-1.0],
    [0.0],
    [0.15]
])
time        = 0.0
state_his   = [state[2].item()] 
time_stamp  = [0.0]



for i in range(60000):
    time += 0.001
    state = state + ecgSSEq(state, time)*0.001
    state_his.append(state[2].item())
    time_stamp.append(time)




plt.plot(time_stamp, state_his)
plt.grid()
plt.show()