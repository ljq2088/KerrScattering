# Handoff Validation, 2026-10-23

The handoff was checked with the following bounded operations:

| Check | Observed result |
|---|---|
| Python test suite, `python -m pytest -q` | 63 passed in 14.23 seconds |
| Existing Schwarzschild quadrature test | Two SciPy integration warnings retained; tests passed |
| Native Linux portable-launcher smoke case | `a=0.5,omega=0.1,ell=m=0,n=1`, completed in 12.62 seconds |
| Smoke vs archived higher-resolution response | Relative changes: `chi=3.31e-51`, `phase=1.49e-50`, `R0=3.22e-51` |
| Current manuscript evidence check | 118 labels, 29 cited sources, 243 abstract words, 8 figures; passed |
| Git-index archive extracted to independent directory | Byte-preserving verification passed under Windows Python and WSL Linux Python |
| Historical precision records | 44 completed, 2 failed, 1 inputs-changed; statuses retained |
| Accepted high-precision pairs | 21 |
| TeX source dependencies | All dependencies of the four handoff documents present |
| Supplied `nonlinear_GF.pdf` | Excluded by filename and exact content hash |
| Credential-pattern scan of selected text files | No matching credential or private-key patterns |

The native Linux smoke case and its complete source snapshot are in
`results/precision_portability_20261023/native_linux_smoke/`.
Julia 1.10.7 ran with one thread and the existing resource guards.

The independent index archive was generated from tree
`67e294fa160183724b93d07489cbb403cd8006bd`. It verified 692 payload files before
this validation note was added. The final file manifest also includes this
note. The manifest excludes itself from its hash list.

The current PRD source SHA256 is
`368c11d4ab6c5ac6ece03ead224db14219689b88f8e41402ceba8112281736ff`.
Its scientific contents and the supplied PDF were preserved during packaging.
The 192 Julia equation, angular-normalization, horizon-phase, and manufactured
Levin checks passed during the preceding numerical completion on this date.

This validation establishes transport integrity, runnable core code, and the
stated internal numerical checks. External scalar high-precision benchmarks,
finite-coupling validation, and final scientific submission review retain the
statuses recorded in `HANDOFF.md`.
