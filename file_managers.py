import re
from datetime import datetime, timedelta

from additional_functions import glonass_day_seconds, gps_week_seconds


class FilesManager:

    def __init__(self, target_system, measurement_file, navigation_file):
        self.target_system = target_system
        self.measurement_file = measurement_file
        self.navigation_file = navigation_file

    def reading_necessary_data_from_header(self):
        approx_position = None
        leap_seconds = None

        with open(self.measurement_file, 'r') as file:
            for line in file:
                if 'APPROX POSITION XYZ' in line:
                    coord_line = line.strip()
                    x, y, z = map(float, coord_line.split()[:3])
                    approx_position = (x, y, z)
                    break

            for line in file:
                if "LEAP SECONDS" in line:
                    leap_str = line[:6].strip()
                    leap_seconds = float(leap_str)
                    break

            return approx_position, leap_seconds

    def read_measurement_file(self, target_time, leap_seconds):
        target_time_str = (
            target_time.strftime('%y%m%d%H%M') + f'{target_time.second}'
        )
        satellites_data = []
        current_satellites = []

        with open(self.measurement_file, 'r') as file:
            for line in file:
                if 'END OF HEADER' in line:
                    break

            for line in file:
                if line[:18].replace(" ", "") == target_time_str:

                    num_satellites_target_time = int(line[30:32])
                    sat_list_str = line[32:].strip()
                    file_iter = iter(file)
                    while len(sat_list_str) < num_satellites_target_time * 3:
                        sat_list_str += next(file_iter).strip()
                    current_satellites = (
                        [sat_list_str[i:i+3]
                         for i in range(0, num_satellites_target_time * 3, 3)]
                    )

                    if self.target_system == 'R':
                        target_time -= timedelta(seconds=leap_seconds)
                        target_time_in_seconds = (
                            glonass_day_seconds(target_time)
                        )
                    else:
                        target_time_in_seconds = (
                            gps_week_seconds(target_time)
                        )

                    for sat in current_satellites:
                        pseudorange_str = next(file)[:17]
                        if sat[0] == self.target_system:
                            pseudorange_str = pseudorange_str.strip()
                            if pseudorange_str:
                                pseudorange = float(pseudorange_str)
                                satellites_data.append((sat[1:], pseudorange,
                                                       target_time_in_seconds))
                            else:
                                print('Отсутствует значение параметра '
                                      'псевдодальности для данного спутника')
                        for _ in range(4):
                            next(file)
                    break

        return satellites_data, target_time

    def finding_nearest_nodal_point(
            self, measurement_time, satellite
    ):
        prev_epoch = None
        time_difference_min = timedelta(days=1)

        with open(self.navigation_file, 'r') as file:
            for line in file:
                if "END OF HEADER" in line:
                    break

            for line in file:
                need_line = line[:2].strip()
                if need_line and int(need_line) == int(satellite):
                    parts = line[:22].split()
                    year = int(parts[1]) + 2000
                    month = int(parts[2])
                    day = int(parts[3])
                    hour = int(parts[4])
                    minute = int(parts[5])
                    second = int(float(parts[6]))
                    epoch_time = datetime(
                        year, month, day, hour, minute, second
                    )
                    time_difference = abs(measurement_time - epoch_time)

                    if time_difference < time_difference_min:
                        prev_epoch = epoch_time
                        time_difference_min = time_difference

        return prev_epoch

    def read_navigation_file(self, target_satellite, target_time):

        def convert_scientific_notation(value_str: str) -> float:
            return float(value_str.replace('D', 'E'))

        block_size = 8 if self.target_system == 'G' else 4

        with open(self.navigation_file, 'r') as file:
            for line in file:
                if 'END OF HEADER' in line:
                    break

            for line in file:
                need_line = line[0:2].strip()
                if need_line and int(need_line) == int(target_satellite):
                    parts = line[:22].split()
                    year = int(parts[1]) + 2000
                    month = int(parts[2])
                    day = int(parts[3])
                    hour = int(parts[4])
                    minute = int(parts[5])
                    second = int(float(parts[6]))

                    epoch_time = datetime(
                        year, month, day, hour, minute, second
                    )

                    if epoch_time == target_time:
                        block_lines = [line.strip()]

                        for _ in range(block_size - 1):
                            line = file.readline().strip()
                            block_lines.append(line)

                        all_values = []
                        all_values.append(epoch_time)
                        for line in block_lines:
                            numbers = re.findall(
                                r'[+-]?\d+\.\d+[DEde][+-]?\d+', line
                            )
                            converted_numbers = [
                                convert_scientific_notation(num)
                                for num in numbers
                            ]
                            all_values.extend(converted_numbers)

                        return all_values
