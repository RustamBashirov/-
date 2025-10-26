import math

import numpy as np

from additional_functions import glonass_day_seconds


class SatelliteLocation:
    """Класс расчета координат спутников"""

    def __init__(self, target_system):
        self.target_system = target_system

    def satellite_location_determination(self, satellite_data):
        """Выбор системы ГНСС"""
        x, y, z, delta_T, pseudorange = (
            self.gps_calculate_satellite_position(*satellite_data)
            if self.target_system == 'G' else
            self.glonass_calculate_satellite_position(*satellite_data)
        )
        return x, y, z, delta_T, pseudorange

    def gps_calculate_satellite_position(
            self, ephemeris_data, pseudorange, T_n
    ):
        """Определения координат спутника GPS"""
        a_f0 = ephemeris_data[1]
        a_f1 = ephemeris_data[2]
        a_f2 = ephemeris_data[3]
        C_rs = ephemeris_data[5]
        delta_n = ephemeris_data[6]
        M0 = ephemeris_data[7]
        C_uc = ephemeris_data[8]
        e = ephemeris_data[9]
        C_us = ephemeris_data[10]
        sqrtA = ephemeris_data[11]
        t_oe = ephemeris_data[12]
        t_oc = ephemeris_data[12]
        C_ic = ephemeris_data[13]
        Omega0 = ephemeris_data[14]
        C_is = ephemeris_data[15]
        i0 = ephemeris_data[16]
        C_rc = ephemeris_data[17]
        omega = ephemeris_data[18]
        OmegaDot = ephemeris_data[19]
        IDOT = ephemeris_data[20]

        c = 299792458.0
        mu = 3.986005e14
        C = -4.442807633e-10
        omega_earth = 7.2921151467e-5

        pr_seconds = pseudorange / c
        T_sat = (T_n - pr_seconds) % 604800

        T_GPS = T_sat

        t_k = T_GPS - t_oe
        n0 = math.sqrt(mu) / (sqrtA ** 3)
        n = n0 + delta_n
        M_k = M0 + n * t_k

        delta_T_R = C * e * sqrtA * math.sin(M_k)
        dt = T_GPS - t_oc
        delta_T = a_f0 + a_f1 * dt + a_f2 * (dt ** 2) + delta_T_R
        T_GPS = T_GPS - delta_T

        t_k = T_GPS - t_oe
        n0 = math.sqrt(mu) / (sqrtA ** 3)
        n = n0 + delta_n
        M_k = M0 + n * t_k

        E_k = M_k
        for _ in range(10):
            E_new = (
                E_k - (E_k - e * math.sin(E_k) - M_k) / (1 - e * math.cos(E_k))
            )
            if abs(E_new - E_k) < 1e-9:
                E_k = E_new
                break
            E_k = E_new

        sin_E_k = math.sin(E_k)
        cos_E_k = math.cos(E_k)
        sqrt_1_e2 = math.sqrt(1 - e**2)

        sin_theta_k = (sqrt_1_e2 * sin_E_k) / (1 - e * cos_E_k)
        cos_theta_k = (cos_E_k - e) / (1 - e * cos_E_k)

        theta_k = math.atan2(sin_theta_k, cos_theta_k)

        Phi_k = theta_k + omega
        delta_U_k = C_uc * math.cos(2 * Phi_k) + C_us * math.sin(2 * Phi_k)
        U_k = Phi_k + delta_U_k

        A_val = sqrtA ** 2
        delta_r_k = C_rc * math.cos(2 * Phi_k) + C_rs * math.sin(2 * Phi_k)
        r_k = A_val * (1 - e * cos_E_k) + delta_r_k

        delta_i_k = C_ic * math.cos(2 * Phi_k) + C_is * math.sin(2 * Phi_k)
        i_k = i0 + delta_i_k + IDOT * t_k

        Omega_k = Omega0 + (OmegaDot - omega_earth) * t_k - omega_earth * t_oe

        cos_U_k = math.cos(U_k)
        sin_U_k = math.sin(U_k)
        cos_Omega_k = math.cos(Omega_k)
        sin_Omega_k = math.sin(Omega_k)
        cos_i_k = math.cos(i_k)
        sin_i_k = math.sin(i_k)

        X_svk = r_k * (cos_U_k * cos_Omega_k - sin_U_k * sin_Omega_k * cos_i_k)
        Y_svk = r_k * (cos_U_k * sin_Omega_k + sin_U_k * cos_Omega_k * cos_i_k)
        Z_svk = r_k * sin_U_k * sin_i_k

        return X_svk, Y_svk, Z_svk, delta_T, pseudorange

    def glonass_calculate_satellite_position(
            self, ephemeris_data, pseudorange, T_n
    ):
        """Определения координат спутника ГЛОНАСС"""
        MU = 398600.44
        R3 = 6378.136
        C20 = -1082.63e-6
        OMEGA3 = 0.7292115e-4
        c = 299792458.0

        dt_utc = ephemeris_data[0]
        tau_j = ephemeris_data[1]
        gamma_j = ephemeris_data[2]

        t_b = glonass_day_seconds(dt_utc)

        s0 = np.array([
            ephemeris_data[4],
            ephemeris_data[8],
            ephemeris_data[12],
            ephemeris_data[5],
            ephemeris_data[9],
            ephemeris_data[13]
        ])

        accel_ext = np.array([
            ephemeris_data[6],
            ephemeris_data[10],
            ephemeris_data[14]
        ])

        def f(t, s):
            x, y, z, vx, vy, vz = s
            r = np.sqrt(x*x + y*y + z*z)
            r3 = r**3
            r5 = r**5
            A = MU / r3

            z2 = z*z
            z2_r2 = 5.0 * z2 / (r*r)
            c20_term = 1.5 * C20 * MU * R3*R3 / r5

            f_vec = np.zeros(6)
            f_vec[0] = vx
            f_vec[1] = vy
            f_vec[2] = vz
            f_vec[3] = (
                (OMEGA3*OMEGA3 - A)*x + 2*OMEGA3*vy +
                c20_term*x*(1 - z2_r2) + accel_ext[0]
            )
            f_vec[4] = (
                (OMEGA3*OMEGA3 - A)*y - 2*OMEGA3*vx
                + c20_term*y*(1 - z2_r2) + accel_ext[1]
            )
            f_vec[5] = -A*z + c20_term*z*(3 - z2_r2) + accel_ext[2]

            return f_vec

        def rk4_step(t, s, h):
            k1 = h * f(t, s)
            k2 = h * f(t + h/2, s + k1/2)
            k3 = h * f(t + h/2, s + k2/2)
            k4 = h * f(t + h, s + k3)
            return s + (k1 + 2*k2 + 2*k3 + k4)/6

        Pi_j = pseudorange / c
        T_j_t_pr = (T_n - Pi_j) % 86400
        T_mdv_t_pr = T_j_t_pr + tau_j - gamma_j * (T_j_t_pr - t_b)
        if T_mdv_t_pr < 0:
            T_mdv_t_pr += 86400

        t_current = t_b
        s_current = s0.copy()
        h = 60.0

        if T_mdv_t_pr > t_b:
            h = abs(h)
        else:
            h = -abs(h)

        while abs(t_current - T_mdv_t_pr) > abs(h):
            s_current = rk4_step(t_current, s_current, h)
            t_current += h

        if t_current != T_mdv_t_pr:
            h_final = T_mdv_t_pr - t_current
            s_current = rk4_step(t_current, s_current, h_final)
            t_current = T_mdv_t_pr

        s_current_scaled = [float(coord) * 1000 for coord in s_current]
        return (
            s_current_scaled[0],
            s_current_scaled[1],
            s_current_scaled[2],
            T_j_t_pr - T_mdv_t_pr,
            pseudorange
        )
