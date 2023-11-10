# cardimetry-dummy-client
Dummy testing client for Cardimetry system with artificial ECG wave generator and MQTT connection. The ECG wave generated refers to the dynamical model proposed by [Patrick E. McSharry et al.](https://web.mit.edu/~gari/www/papers/ieeetbe50p289.pdf).

Run the dummies with the following arguments:
```
python cdc_main.py {DEVICE_NAME} {PATIENT_NAME} {CONDITION}
// {CONDITION} can be filled with "a" for abnormality and "n" for normal
```