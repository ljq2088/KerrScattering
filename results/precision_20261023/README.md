# Scalar Precision Campaign, 2026-10-23

This directory contains newly computed scalar (`s=0`) responses. The original
manuscript's numerical data and figures are unchanged.

## Conventions and Scope

- `M=1`, `a=0.5`, real positive frequency, `exp(-i omega t+i m phi)`.
- New radial calculations use `m=0`, `ell=0,1,2`, and local powers `n=1,2,3`.
- `rho = chi/2 + i phase`; the physical fractional flux and phase shifts
  include the small coupling and incident-amplitude factor.
- The radial grid includes the exact horizon and compactified infinity.
- Current full radial frequencies cover `1e-5` through `10` at the points
  listed in `comparison.csv`. Angular-only checks extend through `100`.
- Paired agreement and off-grid original-equation residuals provide internal
  precision evidence. An external high-precision scalar benchmark remains
  a separate validation task.

## Reproduction

Run the following commands from the repository root in Windows PowerShell.
The launchers use WSL distribution `Ubuntu-22.04-D`, Julia 1.10.7, one thread,
a 300-second limit per radial case, and a 1.5-GB current-RSS guard.
Existing case directories are preserved.

```powershell
python -X utf8 scripts/run_scalar_precision_campaign_20261023.py --suite low --resolution coarse
python -X utf8 scripts/run_scalar_precision_campaign_20261023.py --suite low --resolution fine
python -X utf8 scripts/run_scalar_precision_campaign_20261023.py --suite high --resolution coarse
python -X utf8 scripts/run_scalar_precision_campaign_20261023.py --suite high --resolution fine
python -X utf8 scripts/run_scalar_precision_extra_20261023.py --group power --resolution coarse
python -X utf8 scripts/run_scalar_precision_extra_20261023.py --group power --resolution fine
python -X utf8 scripts/analyze_scalar_precision_20261023.py
```

The original highest-frequency fine run triggered the earlier global-Levin
memory guard. Its successful cellwise-Levin replacement is
`retry_l0_m0_w10_n1_fine`. The `omega=5,n=2` fine launcher was edited while
executing; that run is retained with `inputs-changed` status and excluded.
Its independently rerun replacement is `retry_power_l0_m0_w5_n2_fine`.
The one-case launcher accepts a fresh directory name, frequency, `--n`,
`--ell`, `--quad`, and `--levin` for independent reruns.

## Evidence

Each radial case has `manifest.json`, standard output/error, and
`solution/result.toml`. Successful records include matching input hashes
before/after execution and hashed outputs. `source_*` directories retain
earlier source versions used by completed cases. `comparison.csv` is
regenerated from verified successful records; `summary.json` states the
acceptance thresholds' aggregate outcome. Failed and changed-input runs
remain available for audit.

`angular_wkb_refined.toml` and its manifest record separate angular
truncation checks. Frequencies above `10` in that file are angular-only;
the associated radial WKB estimates are conditional analytical estimates.

The new Chinese review note is
`output/pdf/kerr_precision_flux_phase_20261023.pdf`. The original paper
received narrative-only edits, documented in
`output/overleaf_20261023/editorial_audit.json`.
