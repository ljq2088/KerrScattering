import numpy as np


def bondi_matrix(z, Dz, D2z, l, s):
    """Construct the Bondi-coordinate ODE linear operator.

    ODE: a2(z) * phi'' + a1(z) * phi' + a0(z) * phi = 0
    with a2 = z^2 * (1-z), a1 = z*(2-3z) - s, a0 = -(l*(l+1) + z)

    Args:
        z: (N+1,) grid points.
        Dz: (N+1, N+1) first derivative matrix.
        D2z: (N+1, N+1) second derivative matrix.
        l: angular harmonic index.
        s: ODE parameter (frequency-dependent, complex).

    Returns:
        B: (N+1, N+1) linear operator matrix.
    """
    a2 = z ** 2 * (1 - z)
    a1 = z * (2 - 3 * z) - s
    a0 = -(l * (l + 1) + z)

    B = np.diag(a2) @ D2z + np.diag(a1) @ Dz + np.diag(a0)
    return B
