import numpy as np
from scipy.fft import dct


def cheb(N):
    """Compute N+1 Chebyshev differentiation matrix D and nodes x in [-1,1].

    Args:
        N: number of intervals (polynomial degree).

    Returns:
        D: (N+1, N+1) differentiation matrix.
        x: (N+1,) Chebyshev nodes cos(pi*k/N), k=0..N.
    """
    if N == 0:
        return np.array([[0.0]]), np.array([1.0])

    x = np.cos(np.pi * np.arange(N + 1) / N)
    c = np.ones(N + 1)
    c[0] = 2.0
    c[-1] = 2.0
    c *= (-1.0) ** np.arange(N + 1)

    X = np.tile(x, (N + 1, 1))
    dX = X - X.T
    D = np.outer(c, 1.0 / c) / (dX + np.eye(N + 1))
    D = D - np.diag(np.sum(D, axis=1))
    return D, x


def real_to_cheb(f):
    """Convert function values at Chebyshev nodes to Chebyshev expansion coefficients.

    Uses DCT-II (scipy.fft.dct). For even N, matches MATLAB real_to_cheb exactly.

    Args:
        f: (N+1,) or (N+1, K) array of function values at Chebyshev nodes.

    Returns:
        a: Chebyshev coefficients of same shape as f.
    """
    f = np.atleast_1d(f)
    scalar = f.ndim == 1
    if scalar:
        f = f.reshape(-1, 1)

    N = f.shape[0] - 1

    if N % 2 == 0:
        a = dct(f, type=2, axis=0, norm=None)
        a = 2 * a / N
        a[0, :] /= 2
        a[-1, :] /= 2
    else:
        n = np.arange(N + 1)
        ii, nn = np.meshgrid(n, n)
        A = np.cos(ii * nn * np.pi / N)
        a = np.linalg.solve(A, f)

    if scalar:
        a = a.ravel()
    return a


def cheb_interpolate(a, x1, x2, x):
    """Evaluate Chebyshev interpolant at arbitrary points.

    Args:
        a: (N+1,) or (N+1, K) Chebyshev coefficients on [x1, x2].
        x1, x2: domain endpoints (x1 < x2).
        x: scalar or array of evaluation points.

    Returns:
        vals: interpolated values, same shape convention as input x.
    """
    if x1 >= x2:
        x1, x2 = x2, x1

    a = np.atleast_1d(a)
    if a.ndim == 1:
        a = a.reshape(-1, 1)

    N = a.shape[0] - 1
    n = np.arange(N + 1).reshape(-1, 1)

    xL = x2 - x1
    x = np.asarray(x)
    z = 2 * (x - x1) / xL - 1
    z = np.clip(z, -1, 1)
    theta = np.arccos(z)

    scalar = np.isscalar(x)
    if scalar:
        vals = np.sum(a * np.cos(n * theta), axis=0)
        if vals.size == 1:
            return vals.item()
        return vals

    theta = np.atleast_1d(theta)
    vals = a.T @ np.cos(n * theta)

    if x.ndim == 1 and x.shape[0] > 0:
        pass

    if vals.shape[0] == 1:
        vals = vals.ravel()

    return vals
