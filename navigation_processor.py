from random import randrange
import math

from file_managers import FilesManager
from satellite_data import SatelliteLocation
from reciever_data import RecieverLocation
from additional_functions import calculate_elevation_angle


class NavigationProcessor:

    def __init__(self, target_system, measurement_file, navigation_file):
        self._files_manager = FilesManager(
            target_system, measurement_file, navigation_file
        )
        self._satellite_location = SatelliteLocation(target_system)
        self.reciever_location = RecieverLocation(target_system)
        self._target_system = target_system
        self.approx_position, self.leap_seconds = (
            self._files_manager.reading_necessary_data_from_header()
        )

    def run(self, target_times, number_satellites):
        x_0, y_0, z_0 = self.approx_position
        satellites_data_receiver = []
        for target_time in target_times:
            all_observations, measurement_time_system = (
                self._files_manager.read_measurement_file(
                    target_time, self.leap_seconds
                )
            )
            print('Время формирования измерения', measurement_time_system)
            available_observations = all_observations.copy()
            satellites_data_receiver_target_time = {}
            while (len(satellites_data_receiver_target_time)
                   < number_satellites
                   and available_observations):
                random_index = randrange(len(available_observations))
                satellite, pseudorange, T_pr = (
                    available_observations.pop(random_index)
                )
                nearest_nodal_point_time = (
                    self._files_manager.finding_nearest_nodal_point(
                        measurement_time_system, satellite
                    )
                )
                data = self._files_manager.read_navigation_file(
                    satellite, nearest_nodal_point_time
                )
                if data:
                    sat_data = data, pseudorange, T_pr
                    x_sat, y_sat, z_sat, delta_T_sat, pseudorange = (
                        self._satellite_location
                        .satellite_location_determination(sat_data)
                    )
                    elevation_angle = calculate_elevation_angle(
                        x_0, y_0, z_0, x_sat, y_sat, z_sat
                    )
                    if elevation_angle > 50:
                        print('Время эфемерид', nearest_nodal_point_time,
                              'Номер спутника', satellite,
                              'Угол места', elevation_angle,
                              'Координаты спутника', (x_sat, y_sat, z_sat))
                        satellites_data_receiver_target_time[satellite] = (
                            x_sat, y_sat, z_sat, delta_T_sat, pseudorange
                        )

            if len(satellites_data_receiver_target_time) < number_satellites:
                print('Недостаточно спутников!')
                return None
            satellites_data_receiver.append(
                satellites_data_receiver_target_time
            )

        recieve_xyz = (self.reciever_location.
                       solve_navigation(satellites_data_receiver))
        if recieve_xyz:
            print('Полученные абсолютные погрешности:',
                  recieve_xyz[0] - x_0, recieve_xyz[1] - y_0,
                  recieve_xyz[2] - z_0)
            return (recieve_xyz[0] - x_0,
                    recieve_xyz[1] - y_0,
                    recieve_xyz[2] - z_0)
