import numpy as np
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from additional_functions import round_to_three_decimal


class RecieverLocation:

    def __init__(self, target_system):
        self.target_system = target_system

    def _round_to_three_decimal(self, value):
        """Вспомогательный метод для округления до 3 знаков после запятой"""
        try:
            # Проверка на NaN и бесконечность
            if np.isnan(value) or np.isinf(value):
                return float('nan')
            return float(Decimal(str(value)).quantize(
                Decimal('0.000000000001'),
                rounding=ROUND_HALF_UP
            ))
        except (InvalidOperation, ValueError, TypeError):
            return float('nan')

    def solve_navigation(
            self, satellites_data_list, max_iterations=10, tolerance=1
    ):
        """"Решение навигаицонной задачи при 2 и более спутников"""
        system_multiplier = -1 if self.target_system == 'G' else 1
        c = 299792458.0
        omega_3 = 7.2921151467e-5

        M = len(satellites_data_list)
        # print(M)
        x_s, y_s, z_s = 0.0, 0.0, 0.0
        delta_I_list = [0.0] * M
        iteration_number = 1
        PR = 0

        while True:
            Xi_s = []
            H_s = []

            for i, satellites_data in enumerate(satellites_data_list):

                for _, sat_data in satellites_data.items():
                    x_sat, y_sat, z_sat, clock_bias_sat, pseudorange = sat_data

                    if PR == 1:
                        # print('Пошел!')
                        dx = x_s - x_sat
                        dy = y_s - y_sat
                        dz = z_s - z_sat

                        R_ns_j = np.sqrt(dx**2 + dy**2 + dz**2)
                        tau_j = R_ns_j / c
                        alpha_j = omega_3 * tau_j

                        x_sat_corr = x_sat + y_sat * alpha_j
                        y_sat_corr = y_sat - x_sat * alpha_j
                        x_sat, y_sat = x_sat_corr, y_sat_corr

                    dx = x_s - x_sat
                    dy = y_s - y_sat
                    dz = z_s - z_sat
                    R_ns_j = np.sqrt(dx**2 + dy**2 + dz**2)

                    h_x = dx / R_ns_j
                    h_y = dy / R_ns_j
                    h_z = dz / R_ns_j

                    xi_j = (
                        pseudorange - system_multiplier * c * clock_bias_sat
                        - R_ns_j - delta_I_list[i]
                    )

                    Xi_s.append(xi_j)
                    H_s_row = [h_x, h_y, h_z] + [0.0] * M
                    H_s_row[3 + i] = 1.0
                    H_s.append(H_s_row)

            Xi_s = np.array(Xi_s)
            H_s = np.array(H_s)
            # print(Xi_s)
            # print(H_s)

            try:
                if len(satellites_data_list[0]) == 4:
                    delta_theta_s = np.linalg.inv(H_s) @ Xi_s
                else:
                    delta_theta_s = np.linalg.inv(H_s.T @ H_s) @ H_s.T @ Xi_s
            except Exception:
                print('Ошибка, возможно вырожденная матрица!')
                return None

            print('Поправки равны', delta_theta_s)
            # x_s += delta_theta_s[0]
            # y_s += delta_theta_s[1]
            # z_s += delta_theta_s[2]
            # for i in range(M):
            #     delta_I_list[i] += delta_theta_s[3 + i]
            x_s = round_to_three_decimal(x_s + delta_theta_s[0])
            y_s = round_to_three_decimal(y_s + delta_theta_s[1])
            z_s = round_to_three_decimal(z_s + delta_theta_s[2])
            for i in range(M):
                delta_I_list[i] = round_to_three_decimal(
                    delta_I_list[i] + delta_theta_s[3 + i]
                )
            if (np.isnan(x_s) or np.isnan(y_s) or np.isnan(z_s)):
                print('Ошибка округления координат')
                return None

            if PR == 1:
                PDOP = np.linalg.inv((H_s.T @ H_s))
                print('PDOP равен', np.sqrt(np.sum(np.diag(PDOP)[:3])))
                # print(float(x_s), float(y_s), float(z_s),
                #       [float(x) / c for x in delta_I_list])
                return (float(x_s), float(y_s), float(z_s),
                        [float(x) for x in delta_I_list])

            if (np.linalg.norm(delta_theta_s) < tolerance
               or iteration_number == max_iterations):
                PR = 1
            iteration_number += 1
