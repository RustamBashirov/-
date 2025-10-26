from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from navigation_processor import NavigationProcessor


GNSS_SYSTEM = 'G'
NUMBER_SATELLITES = 3
MEASUREMENT_FILE = 'data/zim20430.25o'
NAVIGATION_FILE_GPS = 'data/zim20430.25n'
NAVIGATION_FILE_GLONASS = 'data/zim20430.25g'
TIME_POINT_MEASUREMENT = datetime(2025, 2, 12, 12, 50, 00)
TIME_FINAL = datetime(2025, 2, 12, 13, 50, 00)
TIME_STEP = 30

TOTAL_POINTS = int(
    (TIME_FINAL - TIME_POINT_MEASUREMENT).total_seconds() // TIME_STEP
)
NAVIGATION_FILE = (
    NAVIGATION_FILE_GPS if GNSS_SYSTEM == 'G' else NAVIGATION_FILE_GLONASS
)

# Формирования значений времени для измерений
if NUMBER_SATELLITES == 2:
    time_array = [[TIME_POINT_MEASUREMENT,
                  TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*i),
                  TIME_POINT_MEASUREMENT + timedelta(seconds=2*TIME_STEP*i)]
                  for i in range(1, TOTAL_POINTS // 2 + 1)]
elif NUMBER_SATELLITES == 3:
    time_array = [[TIME_POINT_MEASUREMENT,
                  TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*i)]
                  for i in range(1, TOTAL_POINTS + 1)]
else:
    time_array = [[TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*i)]
                  for i in range(TOTAL_POINTS)]

navigation_task = NavigationProcessor(
    GNSS_SYSTEM, MEASUREMENT_FILE, NAVIGATION_FILE
)

# Конкретный пример
delta_xyz = (
    navigation_task.run(
        [TIME_POINT_MEASUREMENT,
         TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*2)],
        NUMBER_SATELLITES)
)
print([TIME_POINT_MEASUREMENT])
print(delta_xyz)


# DELTA_X = []
# DELTA_Y = []
# DELTA_Z = []
# delta_t = []
# i = 0
# for time in time_array:
#     delta_xyz = (
#         navigation_task.run(time, NUMBER_SATELLITES)
#     )
#     if delta_xyz:
#         delta_x, delta_y, delta_z = delta_xyz
#         seconds = (time[-1] - TIME_POINT_MEASUREMENT).total_seconds()
#         delta_t.append(seconds)
#         DELTA_X.append(delta_x)
#         DELTA_Y.append(delta_y)
#         DELTA_Z.append(delta_z)
#         i += 1

# print('Количество произведенных измерений', i)
# # График DELTA_X
# plt.figure(figsize=(12, 6))
# plt.plot(delta_t, DELTA_X, 'b-', linewidth=1.5)
# plt.title('Величина ошибки по X')
# plt.ylabel('delta x (м)')
# plt.xlabel('delta t (с)')
# plt.grid(True, alpha=0.3)
# plt.ylim(-100, 100)
# plt.xlim(delta_t[0], delta_t[-1])
# plt.tight_layout()
# plt.show()

# # График DELTA_Y
# plt.figure(figsize=(12, 6))
# plt.plot(delta_t, DELTA_Y, 'r-', linewidth=1.5)
# plt.title('Величина ошибки по Y')
# plt.ylabel('delta y (м)')
# plt.xlabel('delta t (с)')
# plt.grid(True, alpha=0.3)
# plt.ylim(-100, 100)
# plt.xlim(delta_t[0], delta_t[-1])
# plt.tight_layout()
# plt.show()

# # График DELTA_Z
# plt.figure(figsize=(12, 6))
# plt.plot(delta_t, DELTA_Z, 'g-', linewidth=1.5)
# plt.title('Величина ошибки по Z')
# plt.ylabel('delta z (м)')
# plt.xlabel('delta t (с)')
# plt.grid(True, alpha=0.3)
# plt.ylim(-100, 100)
# plt.xlim(delta_t[0], delta_t[-1])
# plt.tight_layout()
# plt.show()
