# Method Summary

## Problem Statement

We solve the frequency-domain radial scattering problem for a scalar field Φ on a Schwarzschild background (M, a=0):

□Φ + λ|Φ|²Φ = 0

After Fourier transform Φ(t,r) → φ_ω(r) e^{-iωt} and decomposition in spherical harmonics (l=0, s-wave), the radial equation takes the Bondi form in compactified coordinate z = 2M/r:

a₂(z) φ'' + a₁(z) φ' + a₀(z) φ = λ S[φ]

with:
- a₂(z) = z²(1-z)
- a₁(z) = z(2-3z) + 4iMω
- a₀(z) = -(l(l+1) + z)
- S[φ] = (nonlinear source from |φ|²φ, computed perturbatively)

## Numerical Method

### 1. Multi-domain Chebyshev Discretization

The domain z ∈ [0, 1] is split at a matching point zp:
- Subdomain I: z ∈ [0, zp] (near infinity)
- Subdomain II: z ∈ [zp, 1] (near horizon)

Each subdomain is discretized with N Chebyshev nodes. For low frequencies (ω < 0.1), a sinh mapping concentrates points near z=1 (horizon) to resolve boundary layer behavior.

### 2. Homogeneous Solutions

Two independent homogeneous (λ=0) solutions are computed:
- φ_in: regular at the horizon (z=1), normalized to φ_in(1) = 1
- φ_down: regular at infinity (z=0), normalized to φ_down(0) = 1

Each is obtained by solving the linear system with the appropriate boundary condition replacing one row of the ODE matrix.

### 3. Green Function Matching

At the matching point zp, the full physical wavefunction ψ(z) = φ(z) exp(-iω x(z)) and its derivative must be continuous. The connection coefficients C_id and C_iu are obtained by solving a 2×2 linear system:

[ψ_down  conj(ψ_down)] [C_id]   [ψ_in]
[ψ'_down conj(ψ'_down)] [C_iu] = [ψ'_in]

The transmission and reflection probabilities are:
- T = 1/|C_id|²
- R = |C_iu|²/|C_id|²

### 4. Nonlinear Corrections

The first-order (in λ) correction to the scattering amplitudes is computed using the Green function method:

A^(1)_out = -λ/W ∫ |φ_in|² φ_in² dz

A^(1)_in = -λ/W ∫ |φ_in|² φ_in φ_up dz

where W = 2iω C_id. The corrected scattering probabilities are:
- T₁ = 2Re(A^(1)_in)/|C_id|²
- R₁ = 2Re(C_iu · conj(A^(1)_out))/|C_id|²

## Tortoise Coordinate

The tortoise coordinate x(z) is defined as:
x(z) = 2M (1/z + log(1-z) - log(z))

with dx/dz = -2M/(z²(1-z)). This coordinate maps the horizon (z=1) to x → -∞ and infinity (z=0) to x → +∞.

## Adaptive Mesh Refinement (AnMR)

For ω < 0.1, the horizon boundary layer becomes very thin in z-coordinate. The sinh mapping:

z(y) = zp + (1-zp) sinh(κ_in(y+1)/2) / sinh(κ_in)

clusters points near z=1 (y=-1). The parameter κ = |log(2Mω)| controls the clustering strength.
