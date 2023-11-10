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
for i in range(10000):

    # Next step
    imu_generator.stepOrientation()

    # Save
    time_stamp.append(imu_generator.getTimeStamp())
    qw_his.append(imu_generator.getOrientationQw())
    qx_his.append(imu_generator.getOrientationQx())
    qy_his.append(imu_generator.getOrientationQy())
    qz_his.append(imu_generator.getOrientationQz())

# Plot
fig, ax = plt.subplots(4, 1)
fig.suptitle('Quaternion Orientation')
ax[0].plot(time_stamp, qw_his, c='r')
ax[0].set_ylabel('$q_w$')
ax[1].plot(time_stamp, qx_his, c='c')
ax[1].set_ylabel('$q_x$')
ax[2].plot(time_stamp, qy_his, c='b')
ax[2].set_ylabel('$q_y$')
ax[3].plot(time_stamp, qz_his, c='g')
ax[3].set_ylabel('$q_z$')
ax[3].set_xlabel('$t$')
ax[0].grid()
ax[1].grid()
ax[2].grid()
ax[3].grid()
plt.show()