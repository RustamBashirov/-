import math
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


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
    elevation_angle_degrees = math.degrees(math.acos(cos_theta)) - 90.0
    return float(Decimal(str(elevation_angle_degrees)).quantize(
        Decimal('0.001'), rounding=ROUND_HALF_UP
    ))


def round_to_three_decimal(value):
    """Вспомогательный метод для округления до 12 знаков после запятой"""
    try:
        # Проверка на NaN и бесконечность
        if np.isnan(value) or np.isinf(value):
            return float('nan')
        return float(Decimal(str(value)).quantize(Decimal('0.000000000001'),
                                                  rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        return float('nan')


print(gps_week_seconds(datetime(2013, 10, 23, 20, 00, 0)))
