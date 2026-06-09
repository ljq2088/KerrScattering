# s=-2 R_in benchmark status

User-requested side task:

```text
s = -2
a = 0.5
l = m = 2
omega = 1e-4 and 10.0
quantity: homogeneous R_in amplitude coefficients
```

Suggested tools:

- low frequency: Mathematica BHPT package
- high frequency: GSN / GeneralizedSasakiNakamura.jl
- angular eigenvalue lambda: `/home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py`

Current environment probe via `cmd /c wsl -d Ubuntu-22.04-D`:

```text
WSL exists.
Julia is available at /home/ljq/julia-1.10.7/bin/julia.
wolframscript/math is not on PATH.
/home/ljq/code/GSN/GeneralizedSasakiNakamura.jl was found.
/home/ljq/code/PINN/SolvingTeukolskyEq_autoencoder/utils/compute_lambda_usage.py was found.
```

The branch now uses two benchmark routes:

```text
High frequency:
  scripts/run_spin_minus2_gsn_benchmark.jl
  output: results/spin_minus2_gsn_highfreq.csv

Low frequency:
  scripts/run_spin_minus2_mathematica_benchmark.wl
  output: results/spin_minus2_mathematica_lowfreq.csv

Three-frequency Python comparison:
  scripts/run_spin_minus2_rin_comparison.py
  output: results/spin_minus2_rin_comparison.csv
```

The GSN runner records `lambda`, `transmission_amplitude`,
`incidence_amplitude`, and `reflection_amplitude` in GSN's
`UNIT_TEUKOLSKY_TRANS` normalization. The lambda values were cross-checked with
`compute_lambda_usage.py`.

The Mathematica runner loads

```text
F:\EMRI\Radial_flow\Radial_Function.wl
```

and calls `ComputeAmplitudesMST`, which uses the BHPT/Teukolsky package's MST
method.

Numerical results:

| route | omega | lambda | incidence amplitude | reflection amplitude |
|---|---:|---:|---:|---:|
| Mathematica MST | 1e-4 | n/a | -1.5435347274666643e20 + 3.416432242244572e20 i | 1.0210782613860754e4 - 2.281376866596801e4 i |
| GSN | 10.0 | -26.85215496939334 | 2.4675049712429978e+01 - 5.0001332607188900e+00 i | -6.4579566171517927e-09 - 8.1445991065750824e-09 i |
| GSN/MST | 0.1 | 3.667320713846837 | -1.1422820427e+05 + 2.3264531432e+05 i | -4.2729694283 - 17.946405113 i |

The low-frequency row is the requested Windows Mathematica/MST benchmark. The
high-frequency row is from GSN. These two routes use different libraries and are
kept separate on purpose.

The scalar `s=0` code in this branch is intentionally separate from the `s=-2`
normalization, because the Teukolsky-Starobinsky identities and radial
asymptotic powers change the meaning of the amplitude coefficients.

Current direct-Teukolsky Python comparison:

| omega | Python method | Binc relative error | Bref relative error | benchmark |
|---:|---|---:|---:|---|
| 10.0 | phase-peeled Chebyshev | 4.0e-7 | 3.4e-1 | GSN |
| 0.1 | high-order asymptotic matching, `r_match=200`, `inf_order=14` | 2.7e-10 | 5.3e-12 | Mathematica MST |
| 1e-4 | high-order asymptotic matching | 2.5e-8 | 9.1e-12 | Mathematica MST |

The high-frequency reflected amplitude is about `1e-8`, so it sits near the
double-precision floor of direct Teukolsky-variable matching.  The stable route
for pushing that row to benchmark precision is to evolve the Sasaki-Nakamura
variable, where the two infinity waves have comparable powers, and then apply
the Teukolsky conversion factors.
