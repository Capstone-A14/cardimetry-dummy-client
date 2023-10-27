import cdc_imu_generator as cdc_imu
import matplotlib.pyplot as plt

# Create IMU generator
imu_generator = cdc_imu.CardimetryIMUGenerator()

# Create holder variables
time_stamp  = [imu_generator.getTimeStamp()]
qw_his      = [imu_generator.getOrientationQw()]
qx_his      = [imu_generator.getOrientationQx()]
qy_his      = [imu_generator.getOrientationQy()]
qz_his      = [imu_generator.getOrientationQz()]

# Loop
for i in range(480000):

    # Next step
    imu_generator.stepOrientation()

    # Save
    time_stamp.append(imu_generator.getTimeStamp())
    qw_his.append(imu_generator.getOrientationQw())
    qx_his.append(imu_generator.getOrientationQx())
    qy_his.append(imu_generator.getOrientationQy())
    qz_his.append(imu_generator.getOrientationQz())

# Plot
plt.plot(time_stamp, qw_his)
plt.plot(time_stamp, qx_his)
plt.plot(time_stamp, qy_his)
plt.plot(time_stamp, qz_his)
plt.grid()
plt.show()