# Source and Artifact Provenance

The repository retains its existing public history and research branch. This
handoff adds the local Kerr scalar manuscripts, first-party numerical code,
numerical outputs, and explanatory notes requested by the repository owner.

- `src/kerr_scalar_precision.jl` is the scalar specialization developed in this
  project. Its numerical organization follows the owner's
  `ljq2088/teukolsky-radial-spectral` audit at commit `1621eb5e379b`.
- `results/precision_20261023/` records newly computed scalar responses.
  External spin-minus-two reference results retain their own provenance and
  are outside the scalar response acceptance table.
- Historical Python/MATLAB implementations, manuscripts, and archived data
  remain in their established locations. Historical generated reports carry
  their original dates and scientific scopes.
- Julia, Python dependencies, Mathematica/BHPT, MATLAB, and GSN installations
  are external dependencies; this handoff does not vendor their installations.
- The supplied Schwarzschild reference `nonlinear_GF.pdf` is excluded by name
  and by its exact SHA256 content digest. References to it in derivation text
  remain as bibliographic context. The Kerr manuscripts with names beginning
  `kerr_scalar_` are the user's project outputs and are included.
- Existing repository archives already in Git history retain their original
  status. No new third-party source archive is added by this handoff.

No new license grant is introduced in this transfer. The file manifest records
the exact distributed bytes and the excluded reference digest. Public access
to the repository and software redistribution licensing are separate matters.
