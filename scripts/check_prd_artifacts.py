"""Check that PRD manuscript input artifacts exist and have expected schemas."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "prd" / "artifact_manifest.json"

FIGURES = [
    ROOT / "figures" / "kerr_scalar_low_frequency_axisymmetric.png",
    ROOT / "figures" / "kerr_scalar_nonlinear_axisymmetric_fig2.png",
    ROOT / "figures" / "kerr_scalar_axisymmetric_accuracy.png",
    ROOT / "figures" / "kerr_scalar_superradiant_response.png",
    ROOT / "figures" / "kerr_scalar_near_extremal_scaling.png",
    ROOT / "figures" / "kerr_scalar_modal_powerlaw_classification.png",
    ROOT / "figures" / "kerr_scalar_power_nonlinearity_l0.png",
    ROOT / "figures" / "kerr_scalar_power_near_extremal_scaling.png",
    ROOT / "figures" / "kerr_scalar_power_bandwidth_hierarchy.png",
    ROOT / "figures" / "kerr_scalar_spin_limit.png",
]

CSV_SCHEMAS = {
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l0.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l1.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l2.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l0.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l1.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l2.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l0.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l1.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l2.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l0.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l1.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l2.csv": [
        "omega", "N", "quad_order", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_control_scan.csv": [
        "label", "scan", "l", "m", "a", "omega", "N_outer", "N_inner",
        "r_match", "quad_order", "A_ref_1", "A_hor_1",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_diagnostics.csv": [
        "label", "l", "m", "a", "omega", "quad_order", "N_outer",
        "N_inner", "r_match", "mapping", "radial_weight_model",
        "radial_integral_method", "angular_coupling",
        "angular_coupling_cos2", "wronskian", "wronskian_relative_error",
        "A_ref_1", "A_hor_1", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_fit_table.csv": [
        "l", "omega_peak", "gamma", "qnm_real", "qnm_imag_abs",
        "peak_rms_over_peak", "peak_r2", "peak_fit_points", "pi_Tfit",
        "Tfit_over_TH_minus_1_abs", "tail_rms_log",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_peak_window_sensitivity.csv": [
        "l", "threshold", "points", "omega_peak", "gamma",
        "peak_rms_over_peak", "peak_r2",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_tail_window_sensitivity.csv": [
        "l", "window", "omega_min", "omega_max", "points", "pi_Tfit",
        "tail_rms_log", "abs_Tfit_over_TH_minus_1",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_tail_model_comparison.csv": [
        "l", "omega_min", "omega_max", "points", "pi_Tfit",
        "power_index", "exp_rms_log", "power_rms_log",
        "hawking_fixed_rms_log", "exp_aicc", "power_aicc",
        "delta_aicc_power_minus_exp", "exp_loo_rms_log",
        "power_loo_rms_log", "max_abs_balance",
    ],
    ROOT / "results" / "kerr_scalar_low_frequency_axisymmetric_acceptance.csv": [
        "l", "lowest_accepted_omega", "highest_displayed_omega",
        "displayed_points", "T0_at_lowest", "T1_at_lowest",
        "abs_balance_at_lowest",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_fits.csv": [
        "l", "quantity", "points", "omega_min", "omega_max", "power",
        "intercept", "R2", "expected_power",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_coefficients.csv": [
        "branch", "subdomain", "k", "abs_coeff", "normalized_abs_coeff",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_residuals.csv": [
        "branch", "subdomain", "sample_kind", "sample_index", "relative_residual",
        "radial_relative_residual", "term_scale",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_quality_summary.csv": [
        "case", "branch", "subdomain", "coeff_tail_ratio",
        "residual_grid", "residual_samples", "max_radial_relative_residual",
        "p95_radial_relative_residual", "median_radial_relative_residual",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_convergence_summary.csv": [
        "case", "N_reference", "N_test_max_relative_A_ref",
        "N_test_max_relative_A_H", "r_match_reference",
        "r_match_test_max_relative_A_ref", "r_match_test_max_relative_A_H",
        "quad_reference", "quad_test_max_relative_A_ref",
        "quad_test_max_relative_A_H", "max_Wronskian_relative_error",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_production_convergence.csv": [
        "label", "config", "N", "quad_order", "A_ref_1", "A_hor_1",
        "T1", "R1", "nonlinear_balance", "rel_A_ref_to_reference",
        "rel_A_hor_to_reference", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_after_mb",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_low_frequency_convergence.csv": [
        "label", "l", "m", "omega", "config", "N", "quad_order",
        "r_match", "mapping", "T1", "R1", "nonlinear_balance",
        "wronskian_relative_error", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_after_mb", "status",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_tail_convergence.csv": [
        "label", "config", "N", "quad_order", "A_ref_1", "A_hor_1",
        "T1", "R1", "nonlinear_balance", "rel_A_ref_to_reference",
        "rel_A_hor_to_reference", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_after_mb",
    ],
    ROOT / "results" / "kerr_scalar_angular_convergence.csv": [
        "case", "l_source", "l_target", "m", "a", "omega", "config",
        "lmax_extra", "angular_quad_order", "lambda_source", "lambda_target",
        "C0", "C2", "max_rel_lambda_to_reference",
        "rel_C0_to_reference", "rel_C2_to_reference",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_channels.csv": [
        "l_source", "l_target", "m", "a", "omega", "angular_coupling",
        "angular_coupling_cos2", "abs_A_ref_1", "abs_A_hor_1",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_channel_convergence.csv": [
        "l_source", "l_target", "N_outer", "quad_order",
        "rel_A_ref_to_reference", "rel_A_hor_to_reference",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_response_N288.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_response_N320.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_near_threshold_N288.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_near_threshold_N320.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_highspin_dense_N288.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_highspin_dense_N320.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "nonlinear_balance", "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_response_accepted.csv": [
        "a", "l", "m", "omega_fraction", "omega", "T0", "T1",
        "horizon_response", "horizon_response_relative_change",
        "direct_flux_accepted", "source_grid",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_threshold_limits.csv": [
        "a", "l", "m", "horizon_response_threshold",
        "horizon_response_relative_change", "T1_over_p_threshold",
        "T1_sign_change_verified", "extrapolation",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_highspin_peaks.csv": [
        "a", "l", "m", "sampled_peak_omega_fraction",
        "sampled_peak_horizon_response", "horizon_response_relative_change",
        "largest_valid_omega_fraction", "note",
    ],
    ROOT / "results" / "kerr_scalar_superradiant_matching_convergence.csv": [
        "a", "l", "m", "omega_fraction", "matching_radii",
        "horizon_response_reference", "horizon_response_relative_spread",
        "max_wronskian_relative_error",
    ],
    ROOT / "results" / "kerr_scalar_spin_limit.csv": [
        "l", "m", "a", "omega", "radial_lambda", "B_inc", "B_ref",
        "T0", "R0", "linear_balance", "T1", "R1", "nonlinear_balance",
        "abs_nonlinear_balance", "flux_normalization_condition_number",
        "wronskian_relative_error", "status",
    ],
}

NEAR_EXTREMAL_THRESHOLD_COLUMNS = [
    "a", "l", "m", "omega_fraction", "p_horizon", "N", "T0", "T1",
    "R1", "linear_balance", "nonlinear_balance", "horizon_response",
    "wronskian_relative_error", "status",
]
for name in [
    "kerr_scalar_newphysics_threshold_N144.csv",
    "kerr_scalar_newphysics_threshold_N176.csv",
    "kerr_scalar_newphysics_extreme_threshold_N144.csv",
    "kerr_scalar_newphysics_extreme_threshold_N176.csv",
    "kerr_scalar_newphysics_highl_threshold_N144.csv",
    "kerr_scalar_newphysics_highl_threshold_N176.csv",
    "kerr_scalar_newphysics_subdominant_threshold_N144.csv",
    "kerr_scalar_newphysics_subdominant_threshold_N176.csv",
]:
    CSV_SCHEMAS[ROOT / "results" / name] = NEAR_EXTREMAL_THRESHOLD_COLUMNS

NEAR_EXTREMAL_SCALING_COLUMNS = [
    "a", "l", "m", "surface_gravity", "detuning_over_kappa",
    "omega_fraction", "p_horizon", "N", "T0", "T1", "R1",
    "linear_balance", "nonlinear_balance", "horizon_response",
    "scaled_horizon_response", "wronskian_relative_error", "status",
]
for name in [
    "kerr_scalar_near_extremal_scaling_N144.csv",
    "kerr_scalar_near_extremal_scaling_N176.csv",
    "kerr_scalar_near_extremal_peakdense_N144.csv",
    "kerr_scalar_near_extremal_peakdense_N176.csv",
    "kerr_scalar_near_extremal_l0_N144.csv",
    "kerr_scalar_near_extremal_l0_N176.csv",
    "kerr_scalar_near_extremal_l0_highspin_N224.csv",
    "kerr_scalar_near_extremal_l0_highspin_N256.csv",
    "kerr_scalar_modal_powerlaw_N144.csv",
    "kerr_scalar_modal_powerlaw_N176.csv",
    "kerr_scalar_modal_powerlaw_extreme_N144.csv",
    "kerr_scalar_modal_powerlaw_extreme_N176.csv",
    "kerr_scalar_modal_powerlaw_subdominant_refine_N224.csv",
    "kerr_scalar_modal_powerlaw_subdominant_refine_N256.csv",
]:
    CSV_SCHEMAS[ROOT / "results" / name] = NEAR_EXTREMAL_SCALING_COLUMNS

CSV_SCHEMAS.update({
    ROOT / "results" / "kerr_scalar_near_extremal_threshold_summary.csv": [
        "a", "l", "m", "surface_gravity", "horizon_response_threshold",
        "scaled_threshold_response", "resolution_relative_change", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_near_extremal_scaling_convergence.csv": [
        "a", "l", "m", "detuning_over_kappa", "horizon_response",
        "scaled_horizon_response", "resolution_relative_change", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_near_extremal_collapse_summary.csv": [
        "l", "m", "detuning_over_kappa", "spin_count",
        "mean_scaled_horizon_response", "relative_standard_deviation",
    ],
    ROOT / "results" / "kerr_scalar_near_extremal_subdominant_summary.csv": [
        "a", "l", "m", "surface_gravity", "horizon_response_threshold",
        "scaled_threshold_response", "resolution_relative_change",
    ],
    ROOT / "results" / "kerr_scalar_near_extremal_peak_summary.csv": [
        "a", "l", "m", "sampled_peak_detuning_over_kappa",
        "sampled_peak_scaled_horizon_response", "resolution_relative_change",
    ],
    ROOT / "results" / "kerr_scalar_near_extremal_mode_crossings.csv": [
        "first_l", "second_l", "lower_spin", "upper_spin",
        "lower_difference", "upper_difference",
    ],
    ROOT / "results" / "kerr_scalar_modal_powerlaw_threshold_values.csv": [
        "a", "l", "m", "surface_gravity", "regime",
        "detuning_over_kappa", "sample_detunings", "horizon_response",
        "scaled_horizon_response", "resolution_relative_change",
        "richardson_relative_correction", "max_linear_balance",
        "max_wronskian_relative_error", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_modal_powerlaw_fixed_y_values.csv": [
        "a", "l", "m", "surface_gravity", "regime",
        "detuning_over_kappa", "horizon_response",
        "scaled_horizon_response", "resolution_relative_change",
        "max_linear_balance", "max_wronskian_relative_error", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_modal_powerlaw_fits.csv": [
        "regime", "l", "m", "detuning_over_kappa", "fit_window",
        "spin_count", "spin_min", "spin_max", "kappa_min", "kappa_max",
        "amplitude", "alpha", "r_squared", "rms_log_residual",
        "max_resolution_relative_change", "extremal_angular_K",
        "conformal_weight_real", "conformal_weight_imag_abs",
        "conformal_class", "classification",
    ],
    ROOT / "results" / "kerr_scalar_modal_powerlaw_model_comparison.csv": [
        "regime", "l", "m", "detuning_over_kappa", "spin_count",
        "pure_power_alpha", "pure_power_amplitude", "pure_power_rss",
        "pure_power_aicc", "finite_limit_c0", "finite_limit_c1",
        "finite_limit_beta", "finite_limit_rss", "finite_limit_aicc",
        "delta_aicc_finite_minus_power", "extremal_angular_K",
        "conformal_weight_real", "conformal_weight_imag_abs",
        "conformal_class", "classification",
    ],
    ROOT / "results" / "kerr_scalar_l0_zero_frequency_summary.csv": [
        "a", "fit_detunings", "zero_frequency_response",
        "analytic_response_ln2_over_pi", "relative_error_to_analytic",
        "max_resolution_relative_change", "max_linear_balance",
        "max_nonlinear_balance", "max_wronskian_relative_error",
        "low_resolution", "high_resolution",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_N144.csv": [
        "l", "m", "a", "omega", "N", "quad_order", "T0", "T1",
        "horizon_response", "infrared_integral", "phase_integral",
        "analytic_response_limit",
        "scaled_T0", "analytic_T0_coefficient", "scaled_T1",
        "analytic_T1_coefficient", "A_hor_1_real", "A_hor_1_imag",
        "scaled_A_hor_1_real", "scaled_A_hor_1_imag",
        "analytic_A_hor_1_real_coefficient",
        "analytic_A_hor_1_imag_coefficient",
        "scaled_A_hor_1_complex_relative_error",
        "relative_horizon_amplitude_real",
        "relative_horizon_amplitude_imag",
        "analytic_relative_horizon_amplitude_real",
        "analytic_relative_horizon_amplitude_imag",
        "relative_horizon_amplitude_complex_relative_error",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_N176.csv": [
        "l", "m", "a", "omega", "N", "quad_order", "T0", "T1",
        "horizon_response", "infrared_integral", "phase_integral",
        "analytic_response_limit",
        "scaled_T0", "analytic_T0_coefficient", "scaled_T1",
        "analytic_T1_coefficient", "A_hor_1_real", "A_hor_1_imag",
        "scaled_A_hor_1_real", "scaled_A_hor_1_imag",
        "analytic_A_hor_1_real_coefficient",
        "analytic_A_hor_1_imag_coefficient",
        "scaled_A_hor_1_complex_relative_error",
        "relative_horizon_amplitude_real",
        "relative_horizon_amplitude_imag",
        "analytic_relative_horizon_amplitude_real",
        "analytic_relative_horizon_amplitude_imag",
        "relative_horizon_amplitude_complex_relative_error",
        "wronskian_relative_error", "status",
    ],
})

POWER_NONLINEARITY_COLUMNS = [
    "nonlinearity_order", "a", "surface_gravity", "frequency_mode",
    "frequency_coordinate", "omega_over_kappa", "omega", "N",
    "quad_order", "angular_coupling", "T0", "T1", "R1",
    "linear_balance", "nonlinear_balance", "horizon_response",
    "response_over_frequency_power", "analytic_low_frequency_coefficient",
    "wronskian_relative_error", "rss_mb_after", "status",
]
for name in [
    "kerr_scalar_power_nonlinearity_l0_fixed_N144.csv",
    "kerr_scalar_power_nonlinearity_l0_fixed_N176.csv",
    "kerr_scalar_power_nonlinearity_l0_kappa_N144.csv",
    "kerr_scalar_power_nonlinearity_l0_kappa_N176.csv",
]:
    CSV_SCHEMAS[ROOT / "results" / name] = POWER_NONLINEARITY_COLUMNS

CSV_SCHEMAS.update({
    ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_fixed_summary.csv": [
        "nonlinearity_order", "a", "predicted_frequency_power",
        "fitted_frequency_power", "power_fit_r2",
        "analytic_low_frequency_coefficient",
        "extrapolated_low_frequency_coefficient",
        "relative_error_to_analytic_coefficient",
        "fit_window_relative_spread", "max_resolution_relative_change",
        "max_linear_balance", "max_wronskian_relative_error",
    ],
    ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_kappa_summary.csv": [
        "nonlinearity_order", "omega_over_kappa", "predicted_kappa_power",
        "fitted_kappa_power_high_spin", "high_spin_fit_r2",
        "fitted_kappa_power_all_spins", "smallest_surface_gravity",
        "scaled_response_at_smallest_surface_gravity",
        "endpoint_relative_error_to_analytic_coefficient",
        "max_resolution_relative_change", "max_linear_balance",
        "max_wronskian_relative_error",
    ],
    ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_spectral_coefficients.csv": [
        "branch", "subdomain", "k", "abs_coeff", "normalized_abs_coeff",
    ],
    ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_spectral_residuals.csv": [
        "branch", "subdomain", "sample_kind", "sample_index",
        "relative_residual", "radial_relative_residual", "term_scale",
    ],
    ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_spectral_quality_summary.csv": [
        "case", "l", "m", "a", "omega", "N", "branch", "subdomain",
        "coeff_tail_ratio", "residual_grid", "residual_samples",
        "max_radial_relative_residual", "p95_radial_relative_residual",
        "median_radial_relative_residual",
    ],
})

POWER_NEAR_EXTREMAL_COLUMNS = [
    "nonlinearity_order", "a", "l", "m", "surface_gravity",
    "detuning_over_kappa", "omega", "p_horizon", "N", "quad_order",
    "angular_coupling_real", "angular_coupling_cos2_real", "B_inc_abs",
    "A_hor_1_real", "T0", "T1", "R1", "linear_balance",
    "nonlinear_balance", "horizon_response", "scaled_horizon_response",
    "wronskian_relative_error", "rss_mb_after", "status",
]
for name in [
    "kerr_scalar_power_near_extremal_N144.csv",
    "kerr_scalar_power_near_extremal_N176.csv",
    "kerr_scalar_power_near_extremal_extreme_N224.csv",
    "kerr_scalar_power_near_extremal_extreme_N256.csv",
    "kerr_scalar_power_near_extremal_additional_N144.csv",
    "kerr_scalar_power_near_extremal_additional_N176.csv",
    "kerr_scalar_power_near_extremal_additional_extreme_N224.csv",
    "kerr_scalar_power_near_extremal_additional_extreme_N256.csv",
    "kerr_scalar_power_near_extremal_dense22_N256.csv",
    "kerr_scalar_power_near_extremal_dense22_N288.csv",
    "kerr_scalar_power_near_extremal_dense33_N256.csv",
    "kerr_scalar_power_near_extremal_dense33_N288.csv",
    "kerr_scalar_power_near_extremal_ultra_principal_N288.csv",
    "kerr_scalar_power_near_extremal_ultra_principal_N320.csv",
    "kerr_scalar_power_band_N256.csv",
    "kerr_scalar_power_band_N288.csv",
    "kerr_scalar_power_peakdense_N288.csv",
    "kerr_scalar_power_peakdense_N320.csv",
]:
    CSV_SCHEMAS[ROOT / "results" / name] = POWER_NEAR_EXTREMAL_COLUMNS

CSV_SCHEMAS.update({
    ROOT / "results" / "kerr_scalar_power_near_extremal_threshold_values.csv": [
        "nonlinearity_order", "a", "l", "m", "surface_gravity", "regime",
        "sample_detunings", "horizon_response", "order_rescaled_response",
        "resolution_relative_change", "richardson_relative_correction",
        "max_linear_balance", "max_nonlinear_relative_balance",
        "max_wronskian_relative_error", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_power_near_extremal_fixed_y_values.csv": [
        "nonlinearity_order", "a", "l", "m", "surface_gravity", "regime",
        "detuning_over_kappa", "horizon_response", "order_rescaled_response",
        "resolution_relative_change", "max_linear_balance",
        "max_nonlinear_relative_balance", "max_wronskian_relative_error",
        "accepted",
    ],
    ROOT / "results" / "kerr_scalar_power_near_extremal_fits.csv": [
        "nonlinearity_order", "regime", "l", "m",
        "detuning_over_kappa", "fit_window", "spin_count", "spin_min",
        "spin_max", "kappa_min", "kappa_max", "amplitude", "alpha",
        "predicted_order_locked_alpha", "alpha_minus_n", "alpha_over_n",
        "r_squared", "rms_log_residual", "max_abs_log_residual",
        "alpha_standard_error", "alpha_ci95_low", "alpha_ci95_high",
        "loo_rms_log_prediction", "loo_max_relative_prediction_error",
        "max_resolution_relative_change",
        "conformal_class", "classification",
    ],
    ROOT / "results" / "kerr_scalar_power_bandwidth_summary.csv": [
        "nonlinearity_order", "a", "l", "m", "surface_gravity",
        "y_min", "y_max", "node_count", "windowed_spectral_weight",
        "rescaled_windowed_weight", "integral_resolution_relative_change",
        "max_point_resolution_relative_change", "max_linear_balance",
        "max_nonlinear_relative_balance", "max_wronskian_relative_error",
        "sampled_peak_y", "accepted",
    ],
    ROOT / "results" / "kerr_scalar_power_bandwidth_fits.csv": [
        "nonlinearity_order", "l", "m", "spin_count", "spin_min",
        "spin_max", "spectral_weight_alpha", "predicted_alpha",
        "alpha_minus_prediction", "innermost_pair_alpha", "r_squared",
        "rescaled_weight_mean", "rescaled_weight_relative_std",
        "rescaled_weight_relative_range",
        "max_integral_resolution_relative_change",
        "max_point_resolution_relative_change",
        "max_nonlinear_relative_balance",
    ],
    ROOT / "results" / "kerr_scalar_power_peak_migration_summary.csv": [
        "nonlinearity_order", "a", "l", "m", "surface_gravity",
        "scan_y_min", "scan_y_max", "scan_spacing", "sampled_peak_y",
        "log_quadratic_peak_y", "log_quadratic_peak_response",
        "local_log_gaussian_sigma", "fit_point_count",
        "max_point_resolution_relative_change", "max_linear_balance",
        "max_nonlinear_relative_balance", "max_wronskian_relative_error",
        "accepted",
    ],
    ROOT / "results" / "kerr_scalar_power_angular_convergence.csv": [
        "nonlinearity_order", "a", "l", "m", "omega", "cos_power",
        "active_lmax_extra", "active_quad_order", "reference_lmax_extra",
        "reference_quad_order", "active_real", "reference_real",
        "relative_change",
    ],
    ROOT / "results" / "kerr_scalar_cft_factorization_samples.csv": [
        "regime", "nonlinearity_order", "a", "l", "m",
        "surface_gravity", "detuning_over_kappa", "B_inc_abs",
        "fixed_incident_horizon_intensity", "horizon_response",
        "scaled_nonlinear_kernel", "conformal_weight_real",
        "conformal_weight_imag_abs", "conformal_class",
        "analytic_intensity_alpha",
    ],
    ROOT / "results" / "kerr_scalar_cft_factorization_fits.csv": [
        "regime", "nonlinearity_order", "l", "m",
        "detuning_over_kappa", "fit_window", "spin_count",
        "kappa_min", "kappa_max", "alpha_response",
        "alpha_intensity", "alpha_kernel", "exponent_closure_error",
        "analytic_intensity_alpha", "conformal_class",
    ],
})

ALL_ARTIFACTS = [*FIGURES, *CSV_SCHEMAS.keys()]


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a valid PNG file")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_figures() -> None:
    for path in FIGURES:
        if not path.exists():
            raise AssertionError(f"Missing figure: {path}")
        if path.stat().st_size < 10_000:
            raise AssertionError(f"Figure is suspiciously small: {path}")
        width, height = png_size(path)
        if width < 600 or height < 300:
            raise AssertionError(
                f"Figure resolution is suspiciously low: {path} ({width}x{height})"
            )


def check_csv(path: Path, required_columns: list[str]) -> None:
    if not path.exists():
        raise AssertionError(f"Missing CSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"CSV has no header: {path}")
        missing = [column for column in required_columns if column not in reader.fieldnames]
        if missing:
            raise AssertionError(f"{path} is missing columns: {', '.join(missing)}")
        row_count = sum(1 for _row in reader)
    if row_count == 0:
        raise AssertionError(f"CSV has no data rows: {path}")


def check_csvs() -> None:
    for path, columns in CSV_SCHEMAS.items():
        check_csv(path, columns)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_manifest() -> None:
    if not MANIFEST.exists():
        raise AssertionError(
            f"Missing artifact manifest: {MANIFEST}. "
            "Run scripts/write_prd_artifact_manifest.py after regenerating PRD inputs."
        )
    with MANIFEST.open(encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("artifacts")
    if not isinstance(entries, list):
        raise AssertionError(f"{MANIFEST} does not contain an 'artifacts' list")

    by_path = {entry.get("path"): entry for entry in entries}
    expected = {relative_path(path) for path in ALL_ARTIFACTS}
    actual = set(by_path)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise AssertionError(f"{MANIFEST} is missing artifacts: {', '.join(missing)}")
    if extra:
        raise AssertionError(f"{MANIFEST} contains unused artifacts: {', '.join(extra)}")

    for path in ALL_ARTIFACTS:
        rel = relative_path(path)
        entry = by_path[rel]
        size = path.stat().st_size
        digest = sha256_file(path)
        if entry.get("size_bytes") != size:
            raise AssertionError(
                f"{rel} size differs from manifest: {size} != {entry.get('size_bytes')}"
            )
        if entry.get("sha256") != digest:
            raise AssertionError(f"{rel} sha256 differs from manifest")


def main() -> None:
    check_figures()
    check_csvs()
    check_manifest()
    print("PRD artifact checks passed.")


if __name__ == "__main__":
    main()
