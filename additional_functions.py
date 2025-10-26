import math
from datetime import datetime, timedelta


def gps_week_seconds(dt):
    weekday = dt.weekday()
    days_to_sunday = (weekday + 1) % 7

    start_of_week = dt - timedelta(
        days=days_to_sunday,
        hours=dt.hour,
        minutes=dt.minute,
        seconds=dt.second,
        microseconds=dt.microsecond
    )

    delta = dt - start_of_week
    return float(delta.total_seconds())


def glonass_day_seconds(dt):
    start_of_day = datetime(dt.year, dt.month, dt.day)
    seconds = (dt - start_of_day).total_seconds()
    return seconds


def calculate_elevation_angle(x_0, y_0, z_0, x_sat, y_sat, z_sat):
    mod_V_r = math.sqrt(x_0**2 + y_0**2 + z_0**2)
    mod_V_s = math.sqrt(x_sat**2 + y_sat**2 + z_sat**2)
    mod_V_rs = (math.sqrt((x_sat - x_0)**2 + (y_sat - y_0)**2
                + (z_sat - z_0)**2))
    cos_theta = ((mod_V_rs**2 + mod_V_r**2 - mod_V_s**2)
                 / (2 * mod_V_rs * mod_V_r))
    # Защита от ошибок округления при вычислениях с плавающей точкой.
    cos_theta = max(min(cos_theta, 1.0), -1.0)
    return math.degrees(math.acos(cos_theta)) - 90.0
