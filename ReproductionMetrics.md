Reproduction metrics:

1. Basic run:
   - scripts/run_reproduction.m must run without manual editing.
   - It must generate results/single_case_result.csv and .mat.

2. Original-script consistency:
   - If the original GF_adaptive_match.m can be run, compare the reorganized code against the original output.
   - Required relative differences:
     T, R, C_id, C_iu < 1e-8;
     T1, R1, Aout1, Ain1 < 1e-6.

3. Matching consistency:
   - Compute the relative value and derivative jumps at the matching point z_p.
   - Require max(value_jump, derivative_jump) < 1e-6.
   - Target value: < 1e-8.

4. Wronskian consistency:
   - Compare the numerical Wronskian with W = 2 i omega C_id, if this relation is valid in the current normalization.
   - Require relative Wronskian error < 1e-6.
   - If the exact Wronskian normalization is ambiguous, report Wronskian variation across the domain instead.

5. Spectral convergence:
   - Run N = 32, 48, 64, 80 for omega = 0.1.
   - Use N = 80 as reference.
   - Require relative changes at N = 64:
       T, R < 1e-8;
       T1, R1 < 1e-5.
   - If not satisfied, report convergence trend instead of claiming success.

6. Frequency sweep:
   - Run omega = 0.01, 0.03, 0.1, 0.3, 1.0.
   - Output omega, N, z_p, T, R, T1, R1, matching_error, W_error, status.
   - Failed cases must be explicitly marked.

7. Quadrature convergence:
   - Test at least two quadgk tolerances.
   - Require T1 and R1 to change by less than 1e-5 when tightening tolerances.

8. Physical sanity:
   - T, R must be finite and non-negative.
   - C_id, C_iu, Aout1, Ain1 must be finite.
   - Do not force T + R = 1 unless the normalization is proven to imply it.