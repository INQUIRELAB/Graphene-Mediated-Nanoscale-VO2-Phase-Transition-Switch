"""Shared Authoritative Model Implementation for GIV-PTS VO2 Switch.

This module provides the authoritative, single-source-of-truth implementation
of the lumped electrothermal reduced-order model (ROM) for the VO2-graphene
Gate-Induced-Volatile Phase-Transition Switch (GIV-PTS).

All simulation scripts (production waveforms, event latency extraction,
convergence checks, energy accounting, hysteresis, and robustness sweeps)
import and use this module.
"""

import os
import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Global physical constants
K_B_EV = 8.617333262145e-5    # Boltzmann constant in eV/K
E_Q = 1.602176634e-19         # Elementary charge in C (and J/eV)
EPS_0 = 8.8541878128e-12      # Vacuum permittivity in F/m
HBAR = 1.054571817e-34        # Reduced Planck constant in J*s
V_F = 1.0e6                   # Fermi velocity of graphene in m/s


class AuthoritativeConfig:
    """Loads and validates the authoritative model configuration."""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # Look relative to this script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cand = script_dir
            config_path = None
            while cand and cand != os.path.dirname(cand):
                p = os.path.join(cand, "authoritative_model_config.json")
                if os.path.exists(p):
                    config_path = p
                    break
                cand = os.path.dirname(cand)
            if config_path is None:
                config_path = os.path.normpath(os.path.join(script_dir, "..", "authoritative_model_config.json"))
            
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Authoritative configuration file NOT found at: {config_path}\n"
                "The configuration file is mandatory. Defaults are not permitted."
            )
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.raw_cfg = json.load(f)
            
        self.config_path = config_path
        self._validate_and_extract()
        
    def _validate_and_extract(self):
        """Validates all required sections and parameters."""
        cfg = self.raw_cfg
        req_sections = [
            "geometry", "materials", "electrical_transport",
            "phase_kinetics", "gate_charge_coupling", "thermal_parameters"
        ]
        for sec in req_sections:
            if sec not in cfg:
                raise ValueError(f"Missing mandatory section '{sec}' in configuration.")
                
        # Geometry
        geo = cfg["geometry"]
        self.L = float(geo["channel_length_L_m"])
        self.W = float(geo["channel_width_W_m"])
        self.t_VO2 = float(geo["channel_thickness_t_VO2_m"])
        self.A_cross = self.W * self.t_VO2
        self.volume_Omega = self.L * self.W * self.t_VO2
        
        # Verify volume consistency: 50 nm x 50 nm x 5 nm = 1.25e-23 m^3
        expected_vol = 1.25e-23
        if not math.isclose(self.volume_Omega, expected_vol, rel_tol=1e-4):
            raise ValueError(f"Channel volume mismatch: calculated {self.volume_Omega} m^3, expected {expected_vol} m^3.")
            
        self.t_ox = float(geo["gate_oxide_thickness_t_ox_m"])
        self.eps_ox_r = float(geo["gate_oxide_relative_permittivity"])
        self.C_top = EPS_0 * self.eps_ox_r / self.t_ox
        
        # Materials
        mat = cfg["materials"]["VO2"]
        self.sigma_ins = float(mat["insulating_conductivity_sigma_ins_S_m"])
        self.sigma_met = float(mat["metallic_conductivity_sigma_met_S_m"])
        self.rho = float(mat["mass_density_rho_kg_m3"])
        self.Cp = float(mat["specific_heat_Cp_J_kg_K"])
        self.fm_crit = float(mat["percolation_threshold_fm"])
        
        # Phase latent heat transformation enthalpy
        self.dH_mit = float(mat.get("latent_heat_dH_J_kg", 51000.0))
        self.m_VO2 = self.rho * self.volume_Omega  # ~5.425e-20 kg
        self.E_latent_total = self.m_VO2 * self.dH_mit  # ~2.767e-15 J (2.767 fJ)
        self.E_latent_switch = self.fm_crit * self.E_latent_total # ~0.922 fJ
        
        # Electrical transport & Circuit
        et = cfg["electrical_transport"]
        pf = et["poole_frenkel_enhancement"]
        self.beta_E = float(pf["beta_E_J_m_V_half"])
        self.E0 = float(pf["E0_regularization_V_m"])
        self.pf_clamp = float(pf["pf_exponent_clamp"])
        self.R_L = float(et["circuit_topology"]["load_resistance_R_L_ohm"])
        
        # Phase kinetics
        pk = cfg["phase_kinetics"]
        bp = pk["barrier_parameters"]
        self.nu = float(pk["attempt_frequency_nu_Hz"])
        self.DG0 = float(bp["ground_state_barrier_DG0_eV"])
        self.T0 = float(bp["transition_temperature_T0_K"])
        self.alpha_th = float(bp["thermal_coupling_alpha_th_eV_K"])
        self.gamma_E = float(bp["kinetic_field_coupling_gamma_E"]["value"])
        if self.gamma_E != 0.0:
            raise ValueError("gamma_E must be strictly 0.0 in authoritative phase kinetics.")
            
        # Gate charge coupling
        gcc = cfg["gate_charge_coupling"]
        self.eta_CT = float(gcc["charge_transfer_efficiency_eta_CT"]["value"])
        kgc = gcc["kinetic_gate_coupling"]
        self.beta_X = float(kgc["carrier_interaction_volume_beta_X_m2"])
        self.alpha_IMTg = float(kgc["alpha_IMTg_eV"])
        self.alpha_MITg = float(kgc["alpha_MITg_eV"])
        
        # Thermal parameters (Configuration-specific!)
        tp = cfg["thermal_parameters"]
        self.T_amb = float(tp["ambient_temperature_T_amb_K"])
        
        off_tp = tp["graphene_off_state"]
        self.R_th_off = float(off_tp["R_th_avg_K_W"])
        self.C_th_off = float(off_tp["C_th_effective_J_K"])
        
        on_tp = tp["graphene_on_state"]
        self.R_th_on = float(on_tp["R_th_avg_K_W"])
        self.C_th_on = float(on_tp["C_th_effective_J_K"])


# Singleton instance
_DEFAULT_CONFIG = None

def get_config(config_path=None):
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None or config_path is not None:
        _DEFAULT_CONFIG = AuthoritativeConfig(config_path)
    return _DEFAULT_CONFIG


def calc_N2D(vg, vd, cfg=None, is_graphene=True, closure_mode="spatially_averaged", clamp_mode="smooth"):
    """Calculates gate-induced carrier density N_VO2 (m^-2).
    
    N_VO2 = eta_CT * N2D_raw where eta_CT is applied exactly once.
    closure_mode: 'spatially_averaged' (integral across x in [0, L]) or 'midpoint' (V_G - V_D / 2).
    clamp_mode: 'smooth' (with delta_V = 0.01 V regularization) or 'hard' (max(0, V_eff)).
    """
    if cfg is None:
        cfg = get_config()
    if not is_graphene or abs(vg) < 1e-9:
        return 0.0
        
    a = E_Q / cfg.C_top
    b = HBAR * V_F * math.sqrt(math.pi) / E_Q  # ~1.1663e-9 V*m

    def _eval_raw_n2d(v_eff):
        if clamp_mode == "hard":
            v_unipolar = max(0.0, v_eff)
        else:
            v_unipolar = 0.5 * (v_eff + math.sqrt(v_eff**2 + 1.0e-4))
        c_val = -v_unipolar
        if c_val >= 0.0:
            return 0.0
        discriminant = b**2 - 4.0 * a * c_val
        sqrt_N2D = (-b + math.sqrt(discriminant)) / (2.0 * a)
        return sqrt_N2D**2

    if closure_mode == "midpoint":
        vg_eff = vg - vd / 2.0
        return cfg.eta_CT * _eval_raw_n2d(vg_eff)
    else:
        # Spatially averaged closure: numerical integration over linear potential V(x) = (x/L)*vd
        n_pts = 21
        x_norm = np.linspace(0.0, 1.0, n_pts)
        n_vals = np.array([_eval_raw_n2d(vg - xn * vd) for xn in x_norm])
        trap_fn = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        n_avg = trap_fn(n_vals, x_norm)
        return cfg.eta_CT * float(n_avg)


def poole_frenkel_conductivity(vd, T, cfg=None):
    """Calculates field-enhanced insulating conductivity sigma_ins_PF.
    
    E_reg = sqrt(E_field^2 + E0^2)
    PF_exponent = min(beta_E * sqrt(E_reg) / (e_q * k_B_eV * T), clamp)
    sigma_ins_PF = sigma_ins * exp(PF_exponent)
    """
    if cfg is None:
        cfg = get_config()
    E_field = vd / cfg.L
    E_reg = math.sqrt(E_field**2 + cfg.E0**2)
    pf_arg = min((cfg.beta_E * math.sqrt(E_reg) / E_Q) / (K_B_EV * T), cfg.pf_clamp)
    return cfg.sigma_ins * math.exp(pf_arg), E_reg, pf_arg


def solve_device_state(v_app, fm, T, cfg=None, ema_model="3D", enable_shunt=False, R_shunt=1900.0):
    """Solves the resistive load-line self-consistently:
    V_app = V_D + R_L * I_tot
    
    ema_model: '3D' (Bruggeman symmetric, fc = 1/3) or '2D' (Bruggeman symmetric, fc = 1/2)
    enable_shunt: If True, adds parallel graphene branch I_gr = V_D / R_shunt into load line.
    
    Returns (vd, id_tot, R_dev, sigma_eff, E_reg, pf_exponent).
    """
    if cfg is None:
        cfg = get_config()
        
    def _calc_sigma_eff(vd_val):
        sigma_ins_pf, E_reg, pf_arg = poole_frenkel_conductivity(vd_val, T, cfg)
        if ema_model == "2D":
            # 2D Bruggeman symmetric EMA: fc = 1/2
            A_2D = (2.0 * fm - 1.0) * cfg.sigma_met + (1.0 - 2.0 * fm) * sigma_ins_pf
            sigma_eff = (A_2D + math.sqrt(A_2D**2 + 4.0 * sigma_ins_pf * cfg.sigma_met)) / 2.0
        else:
            # 3D Bruggeman symmetric EMA: fc = 1/3
            A_ema = (3.0 * fm - 1.0) * cfg.sigma_met + (2.0 - 3.0 * fm) * sigma_ins_pf
            sigma_eff = (A_ema + math.sqrt(A_ema**2 + 8.0 * sigma_ins_pf * cfg.sigma_met)) / 4.0
        return sigma_eff, E_reg, pf_arg

    if v_app <= 1e-9:
        sigma_eff, E_reg, _ = _calc_sigma_eff(0.0)
        R_dev = cfg.L / (sigma_eff * cfg.A_cross)
        return 0.0, 0.0, R_dev, sigma_eff, cfg.E0, 0.0
        
    def residual(vd_guess):
        sigma_eff, _, _ = _calc_sigma_eff(vd_guess)
        R_dev = cfg.L / (sigma_eff * cfg.A_cross)
        if enable_shunt:
            R_eq = (R_dev * R_shunt) / (R_dev + R_shunt)
            return v_app * R_eq / (R_eq + cfg.R_L) - vd_guess
        else:
            return v_app * R_dev / (R_dev + cfg.R_L) - vd_guess
            
    vd = brentq(residual, 0.0, v_app)
    
    sigma_eff, E_reg, pf_arg = _calc_sigma_eff(vd)
    R_dev = cfg.L / (sigma_eff * cfg.A_cross)
    
    if enable_shunt:
        R_eq = (R_dev * R_shunt) / (R_dev + R_shunt)
        id_tot = v_app / (R_eq + cfg.R_L)
    else:
        id_tot = v_app / (R_dev + cfg.R_L)
    
    return vd, id_tot, R_dev, sigma_eff, E_reg, pf_arg


def pulse_waveform(t, amplitude=6.35, t_start=0.5e-9, t_end=2.5e-9, rise_inv=1e12):
    """Smooth sigmoidal pulse with 1 ps rise/fall edge."""
    arg_on = np.clip(-rise_inv * (t - t_start), -100.0, 100.0)
    arg_off = np.clip(-rise_inv * (t - t_end), -100.0, 100.0)
    r_on = 1.0 / (1.0 + np.exp(arg_on))
    r_off = 1.0 / (1.0 + np.exp(arg_off))
    return amplitude * (r_on - r_off)


def ramp_waveform(t, max_voltage=8.0, ramp_period=100.0e-9):
    """Triangular ramp waveform (0 -> max_voltage -> 0 V)."""
    t_half = ramp_period / 2.0
    if t <= t_half:
        return max_voltage * (t / t_half)
    elif t <= ramp_period:
        return max_voltage * (2.0 - t / t_half)
    else:
        return 0.0


def initial_metallic_fraction(vg, cfg=None, is_graphene=True, closure_mode="spatially_averaged", 
                              clamp_mode="smooth", alpha_IMTg=None, alpha_MITg=None):
    """Equilibrium metallic fraction fm at zero bias and T = 300 K."""
    if cfg is None:
        cfg = get_config()
    a_imt = cfg.alpha_IMTg if alpha_IMTg is None else float(alpha_IMTg)
    a_mit = cfg.alpha_MITg if alpha_MITg is None else float(alpha_MITg)
    
    N_VO2 = calc_N2D(vg, 0.0, cfg, is_graphene=is_graphene, closure_mode=closure_mode, clamp_mode=clamp_mode)
    dXg = cfg.beta_X * N_VO2
    A_IMT0 = cfg.DG0 - cfg.alpha_th * (cfg.T_amb - cfg.T0) - a_imt * dXg
    A_MIT0 = cfg.DG0 + cfg.alpha_th * (cfg.T_amb - cfg.T0) + a_mit * dXg
    dG_IMT0 = 0.5 * (A_IMT0 + math.sqrt(A_IMT0**2 + 2.5e-5))
    dG_MIT0 = 0.5 * (A_MIT0 + math.sqrt(A_MIT0**2 + 2.5e-5))
    return 1.0 / (1.0 + math.exp((dG_IMT0 - dG_MIT0) / (K_B_EV * cfg.T_amb)))


def create_ode_system(vg, v_app_func, cfg=None, is_graphene=True, R_tbr_add=0.0,
                      closure_mode="spatially_averaged", clamp_mode="smooth",
                      include_latent_heat=True, ema_model="3D",
                      alpha_IMTg=None, alpha_MITg=None,
                      enable_shunt=False, R_shunt=1900.0,
                      init_mode="gate_specific", t_gate_start=0.5e-9):
    """Creates the right-hand-side function for solve_ivp with full physical couplings.
    
    Includes:
    - Configuration-specific R_th and C_th
    - Explicit latent heat transformation enthalpy: m_VO2 * dH_mit * (dfm/dt)
    - Spatially averaged or midpoint gate closure
    - Smooth or hard gate clamp
    - 3D or 2D effective medium approximation
    - Independent alpha_IMTg and alpha_MITg couplings
    - Optional parallel graphene electrical shunt branch
    - Gate initialization mode (gate-specific pre-relaxation vs controlled common pre-pulse state)
    """
    if cfg is None:
        cfg = get_config()
        
    R_th = cfg.R_th_on if is_graphene else cfg.R_th_off
    C_th = cfg.C_th_on if is_graphene else cfg.C_th_off
    R_th_total = R_th + R_tbr_add
    
    a_imt = cfg.alpha_IMTg if alpha_IMTg is None else float(alpha_IMTg)
    a_mit = cfg.alpha_MITg if alpha_MITg is None else float(alpha_MITg)
    
    def odes(t, y):
        fm, T = y
        v_app = float(v_app_func(t))
        
        vd, id_tot, R_dev, _, _, _ = solve_device_state(
            v_app, fm, T, cfg, ema_model=ema_model, enable_shunt=enable_shunt, R_shunt=R_shunt
        )
        P_joule = vd * id_tot
        
        # Effective gate voltage at current time
        if init_mode == "controlled_common" and t < t_gate_start:
            vg_act = 0.0
        else:
            vg_act = vg
            
        # Gate carrier density
        N_VO2 = calc_N2D(vg_act, vd, cfg, is_graphene=is_graphene, 
                         closure_mode=closure_mode, clamp_mode=clamp_mode)
        dXg = cfg.beta_X * N_VO2
        
        # Phase kinetic barriers
        A_IMT = cfg.DG0 - cfg.alpha_th * (T - cfg.T0) - a_imt * dXg
        A_MIT = cfg.DG0 + cfg.alpha_th * (T - cfg.T0) + a_mit * dXg
        
        dG_IMT = 0.5 * (A_IMT + math.sqrt(A_IMT**2 + 2.5e-5))
        dG_MIT = 0.5 * (A_MIT + math.sqrt(A_MIT**2 + 2.5e-5))
        
        arg_IMT = max(-100.0, min(100.0, -dG_IMT / (K_B_EV * T)))
        arg_MIT = max(-100.0, min(100.0, -dG_MIT / (K_B_EV * T)))
        
        rate_IMT = cfg.nu * math.exp(arg_IMT)
        rate_MIT = cfg.nu * math.exp(arg_MIT)
        
        dfm_dt = (1.0 - fm) * rate_IMT - fm * rate_MIT
        
        # Coupled heat equation with explicit phase enthalpy (latent heat)
        if include_latent_heat:
            dT_dt = (P_joule - (T - cfg.T_amb) / R_th_total - cfg.m_VO2 * cfg.dH_mit * dfm_dt) / C_th
        else:
            dT_dt = (P_joule - (T - cfg.T_amb) / R_th_total) / C_th
            
        return [dfm_dt, dT_dt]
        
    return odes


def solve_transient(vg, v_app_func, t_span=(0.0, 4.0e-9), cfg=None, 
                    is_graphene=True, R_tbr_add=0.0, rtol=1e-8, atol=1e-10, 
                    t_eval=None, max_step=None, events=None,
                    closure_mode="spatially_averaged", clamp_mode="smooth",
                    include_latent_heat=True, ema_model="3D",
                    alpha_IMTg=None, alpha_MITg=None,
                    enable_shunt=False, R_shunt=1900.0,
                    init_mode="gate_specific", t_gate_start=0.5e-9, y0=None):
    """Runs a stiff ODE transient simulation using Radau method."""
    if cfg is None:
        cfg = get_config()
    if max_step is None:
        max_step = (t_span[1] - t_span[0]) / 200.0
        
    if y0 is None:
        if init_mode == "controlled_common":
            fm_0 = initial_metallic_fraction(0.0, cfg, is_graphene=is_graphene,
                                             closure_mode=closure_mode, clamp_mode=clamp_mode,
                                             alpha_IMTg=alpha_IMTg, alpha_MITg=alpha_MITg)
        else:
            fm_0 = initial_metallic_fraction(vg, cfg, is_graphene=is_graphene,
                                             closure_mode=closure_mode, clamp_mode=clamp_mode,
                                             alpha_IMTg=alpha_IMTg, alpha_MITg=alpha_MITg)
        y0 = [fm_0, cfg.T_amb]
    
    odes = create_ode_system(
        vg, v_app_func, cfg, is_graphene=is_graphene, R_tbr_add=R_tbr_add,
        closure_mode=closure_mode, clamp_mode=clamp_mode,
        include_latent_heat=include_latent_heat, ema_model=ema_model,
        alpha_IMTg=alpha_IMTg, alpha_MITg=alpha_MITg,
        enable_shunt=enable_shunt, R_shunt=R_shunt,
        init_mode=init_mode, t_gate_start=t_gate_start
    )
    
    sol = solve_ivp(
        odes, t_span, y0, method="Radau",
        t_eval=t_eval, rtol=rtol, atol=atol,
        max_step=max_step, events=events
    )
    
    if not sol.success:
        raise RuntimeError(f"Solver failed: {sol.message} (rtol={rtol}, atol={atol})")
        
    return sol


def compute_derived_trace(t_arr, fm_arr, T_arr, vg, v_app_func, cfg=None, 
                          is_graphene=True, ema_model="3D", enable_shunt=False, R_shunt=1900.0):
    """Computes all electrical and load-line quantities across a simulated trajectory.
    
    Returns a dictionary of numpy arrays with load-line residual check.
    """
    if cfg is None:
        cfg = get_config()
        
    N = len(t_arr)
    v_app_arr = np.zeros(N)
    vd_arr = np.zeros(N)
    id_arr = np.zeros(N)
    R_dev_arr = np.zeros(N)
    sigma_eff_arr = np.zeros(N)
    E_reg_arr = np.zeros(N)
    pf_arg_arr = np.zeros(N)
    load_line_res_arr = np.zeros(N)
    E_latent_arr = np.zeros(N)
    
    fm_0 = fm_arr[0]
    
    for i in range(N):
        t = t_arr[i]
        fm = fm_arr[i]
        T = T_arr[i]
        v_app = float(v_app_func(t))
        v_app_arr[i] = v_app
        
        vd, id_tot, R_dev, sigma_eff, E_reg, pf_arg = solve_device_state(
            v_app, fm, T, cfg, ema_model=ema_model, enable_shunt=enable_shunt, R_shunt=R_shunt
        )
        vd_arr[i] = vd
        id_arr[i] = id_tot
        R_dev_arr[i] = R_dev
        sigma_eff_arr[i] = sigma_eff
        E_reg_arr[i] = E_reg
        pf_arg_arr[i] = pf_arg
        
        # Load line check: V_app = V_D + R_L * I_D
        load_line_res_arr[i] = abs(v_app - (vd + cfg.R_L * id_tot))
        
        # Latent enthalpy absorbed: m_VO2 * dH_mit * (fm - fm_0)
        E_latent_arr[i] = cfg.m_VO2 * cfg.dH_mit * (fm - fm_0)
        
    return {
        "t": t_arr,
        "V_app": v_app_arr,
        "V_D": vd_arr,
        "I_D": id_arr,
        "R_dev": R_dev_arr,
        "sigma_eff": sigma_eff_arr,
        "E_reg": E_reg_arr,
        "pf_exponent": pf_arg_arr,
        "load_line_residual": load_line_res_arr,
        "fm": fm_arr,
        "T_avg": T_arr,
        "E_latent_J": E_latent_arr
    }


def compute_circuit_energies(t_arr, v_app_arr, vd_arr, id_arr, vg=0.0, 
                             t_event=None, cfg=None, fm_arr=None):
    """Computes circuit energy components and validates energy conservation.
    
    E_dev = integral(V_D * I_D dt)
    E_res = integral(R_L * I_D^2 dt)
    E_src = integral(V_app * I_D dt)
    E_dev_switch = integral_0^t_event(V_D * I_D dt)
    E_latent_event = m_VO2 * dH_mit * (fm(t_event) - fm(0))
    E_gate = 0.5 * C_gate * V_G^2
    """
    if cfg is None:
        cfg = get_config()
        
    p_dev = vd_arr * id_arr
    p_res = cfg.R_L * (id_arr**2)
    p_src = v_app_arr * id_arr
    
    trap_fn = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    E_dev_total = trap_fn(p_dev, t_arr)
    E_res_total = trap_fn(p_res, t_arr)
    E_src_total = trap_fn(p_src, t_arr)
    
    circuit_sum = E_dev_total + E_res_total
    energy_balance_rel_err = abs(E_src_total - circuit_sum) / max(E_src_total, 1e-18)
    
    E_dev_switch = None
    E_src_switch = None
    E_latent_switch = None
    E_latent_switch_discrete = None
    
    if t_event is not None and t_event > t_arr[0]:
        mask = t_arr <= t_event
        if np.sum(mask) >= 2:
            t_sub = t_arr[mask]
            if t_sub[-1] < t_event:
                t_sub = np.append(t_sub, t_event)
                p_dev_sub = np.append(p_dev[mask], np.interp(t_event, t_arr, p_dev))
                p_src_sub = np.append(p_src[mask], np.interp(t_event, t_arr, p_src))
            else:
                p_dev_sub = p_dev[mask]
                p_src_sub = p_src[mask]
            E_dev_switch = trap_fn(p_dev_sub, t_sub)
            E_src_switch = trap_fn(p_src_sub, t_sub)
            
            if fm_arr is not None:
                fm_event = np.interp(t_event, t_arr, fm_arr)
                E_latent_switch_discrete = cfg.m_VO2 * cfg.dH_mit * (fm_event - fm_arr[0])
                # Exact analytical latent energy to continuous percolation threshold (fm = 1/3)
                E_latent_switch = cfg.m_VO2 * cfg.dH_mit * (1.0 / 3.0 - fm_arr[0])
            else:
                E_latent_switch_discrete = None
                E_latent_switch = cfg.E_latent_switch
                
    A_gate = cfg.W * cfg.L
    C_gate_geom = cfg.C_top * A_gate
    E_gate = 0.5 * C_gate_geom * (vg**2)
    
    return {
        "E_dev_total_J": E_dev_total,
        "E_res_total_J": E_res_total,
        "E_src_total_J": E_src_total,
        "energy_balance_rel_err": energy_balance_rel_err,
        "E_dev_switch_J": E_dev_switch,
        "E_src_switch_J": E_src_switch,
        "E_latent_switch_J": E_latent_switch,
        "E_latent_switch_discrete_J": E_latent_switch_discrete,
        "C_gate_geom_F": C_gate_geom,
        "E_gate_J": E_gate
    }
