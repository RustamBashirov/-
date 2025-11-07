from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from math import hypot

from navigation_processor import NavigationProcessor


GNSS_SYSTEM = 'R'
NUMBER_SATELLITES = 2
MEASUREMENT_FILE = 'data/log1023b.13o'
NAVIGATION_FILE_GPS = 'data/log1023b.13N'
NAVIGATION_FILE_GLONASS = 'data/log1023b.13G'
TIME_POINT_MEASUREMENT = datetime(2013, 10, 23, 14, 0, 0)
TIME_FINAL = datetime(2013, 10, 23, 14, 28, 0)
TIME_STEP = 2

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
                  for i in range(10, TOTAL_POINTS // 2 + 1)]
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
i = 20
if NUMBER_SATELLITES == 2:
    example = [[TIME_POINT_MEASUREMENT,
               TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*i),
               TIME_POINT_MEASUREMENT + timedelta(seconds=2*TIME_STEP*i)],
               NUMBER_SATELLITES]
elif NUMBER_SATELLITES == 3:
    example = [[TIME_POINT_MEASUREMENT,
               TIME_POINT_MEASUREMENT + timedelta(seconds=TIME_STEP*i)],
               NUMBER_SATELLITES]
else:
    example = [[TIME_POINT_MEASUREMENT],
               NUMBER_SATELLITES]
delta_xyz = (
    navigation_task.run(*example)
)
print(example)
print(delta_xyz)


(DELTA_X, DELTA_Y, DELTA_Z, ERROR_VECTOR_LENGTH, delta_t) = [], [], [], [], []
i = 0
for time in time_array:
    delta_xyz = (
        navigation_task.run(time, NUMBER_SATELLITES)
    )
    if delta_xyz:
        delta_x, delta_y, delta_z = delta_xyz
        seconds = (time[-1] - TIME_POINT_MEASUREMENT).total_seconds()
        error_length = hypot(delta_x, delta_y, delta_z)
        delta_t.append(seconds)
        DELTA_X.append(delta_x)
        DELTA_Y.append(delta_y)
        DELTA_Z.append(delta_z)
        ERROR_VECTOR_LENGTH.append(error_length)
        i += 1
print('Количество произведенных измерений', i)

# График DELTA_X
plt.figure(figsize=(12, 6))
plt.plot(delta_t, DELTA_X, 'b-', linewidth=1.5)
plt.title('Величина ошибки по X')
plt.ylabel('delta x (м)')
plt.xlabel('delta t (с)')
plt.grid(True, alpha=0.3)
plt.ylim(-5000, 5000)
plt.xlim(delta_t[0], delta_t[-1])
plt.tight_layout()
plt.show()

# График DELTA_Y
plt.figure(figsize=(12, 6))
plt.plot(delta_t, DELTA_Y, 'r-', linewidth=1.5)
plt.title('Величина ошибки по Y')
plt.ylabel('delta y (м)')
plt.xlabel('delta t (с)')
plt.grid(True, alpha=0.3)
plt.ylim(-5000, 5000)
plt.xlim(delta_t[0], delta_t[-1])
plt.tight_layout()
plt.show()

# График DELTA_Z
plt.figure(figsize=(12, 6))
plt.plot(delta_t, DELTA_Z, 'g-', linewidth=1.5)
plt.title('Величина ошибки по Z')
plt.ylabel('delta z (м)')
plt.xlabel('delta t (с)')
plt.grid(True, alpha=0.3)
plt.ylim(-5000, 5000)
plt.xlim(delta_t[0], delta_t[-1])
plt.tight_layout()
plt.show()

# График ERROR_VECTOR_LENGTH
plt.figure(figsize=(12, 6))
plt.plot(delta_t, ERROR_VECTOR_LENGTH, 'g-', linewidth=1.5)
plt.title('Величина длины вектора ошибки')
plt.ylabel('error vector length (м)')
plt.xlabel('delta t (с)')
plt.grid(True, alpha=0.3)
plt.ylim(0, 5000)
plt.xlim(delta_t[0], delta_t[-1])
plt.tight_layout()
plt.show()
