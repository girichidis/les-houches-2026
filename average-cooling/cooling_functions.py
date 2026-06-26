import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import k as k_B_SI
from scipy.optimize import brentq
from scipy.interpolate import interp1d

# Boltzmann constant in cgs: erg / K
k_B = k_B_SI * 1e7

# seconds per Myr
Myr = 1e6 * 365.25 * 24 * 3600


def cool_Lambda(T):
    """
    Cooling function Lambda(T) in erg cm^3 s^-1.

    Works for scalars and NumPy arrays.
    """
    T = np.asarray(T, dtype=float)

    Gamma = 2e-26

    low = (
        1e7 * np.exp(-118400.0 / (T + 1000.0))
        + 1.4e-2 * np.sqrt(T) * np.exp(-92.0 / T)
    )

    mid = (
        5e3
        + 1.4e-2 * np.sqrt(T) * np.exp(-92.0 / T)
    )

    high = (
        3.75e4
        * (1.0 - np.tanh((T - 2e5) / 2e5))
        * np.exp(-5e4 / T)
        + 1e3 * np.exp(-5e4 / T)
    )

    res = np.where(T <= 14577.0, low,
          np.where(T <= 19449.0, mid, high))

    return Gamma * res


def volumetric_cooling_rate(T, n):
    """
    Volumetric cooling rate:
        C = n^2 Lambda(T)

    Units: erg cm^-3 s^-1
    """
    return n**2 * cool_Lambda(T)


def cooling_time(T, n_e):
    """
    Cooling time:
        t_cool = 3 k_B T / (n_e Lambda)

    Units: seconds
    """
    return 3.0 * k_B * T / (n_e * cool_Lambda(T))



def make_equilibrium_temperature_function(
    Tmin=10.0,
    Tmax=1e8,
    NT=20000,
    nmin=1e-4,
    nmax=1e4,
    Nn=2000,
    Gamma=2e-26,
):
    """
    Precompute T_eq(n) from

        n Lambda(T_eq) = Gamma

    and return an interpolation function.

    This is much faster than root-finding for every cell.
    """

    n_grid = np.logspace(np.log10(nmin), np.log10(nmax), Nn)
    T_eq = np.zeros_like(n_grid)

    def equilibrium_function(T, n):
        return n * cool_Lambda(T) - Gamma

    for i, n in enumerate(n_grid):
        try:
            T_eq[i] = brentq(
                equilibrium_function,
                Tmin,
                Tmax,
                args=(n,),
                maxiter=200,
            )
        except ValueError:
            T_eq[i] = np.nan

    valid = np.isfinite(T_eq)

    T_eq_of_n = interp1d(
        np.log10(n_grid[valid]),
        np.log10(T_eq[valid]),
        bounds_error=False,
        fill_value="extrapolate",
    )

    def temperature_from_density(n):
        n = np.asarray(n, dtype=float)
        return 10.0 ** T_eq_of_n(np.log10(n))

    return temperature_from_density, n_grid, T_eq

    import numpy as np
from scipy.interpolate import interp1d

def make_heating_from_equilibrium_temperature(
    n_data,
    Teq_data,
    cool_Lambda,
    kind="linear",
    extrapolate=False,
):
    """
    Construct Gamma(n) from a given equilibrium temperature curve Teq(n).

    Assumes equilibrium condition

        n * Lambda(Teq) = Gamma(n)

    where Gamma is the heating rate per particle [erg s^-1].

    The volumetric heating rate is

        H(n) = n * Gamma(n) = n^2 Lambda(Teq).

    Parameters
    ----------
    n_data : array
        Number density values [cm^-3].
    Teq_data : array
        Equilibrium temperatures [K].
    cool_Lambda : function
        Cooling function Lambda(T) [erg cm^3 s^-1].
    kind : str
        Interpolation type for log Teq(log n).
    extrapolate : bool
        Whether to extrapolate outside the supplied density range.

    Returns
    -------
    Gamma_of_n : function
        Heating rate per particle Gamma(n) [erg s^-1].
    Hvol_of_n : function
        Volumetric heating rate H(n) [erg cm^-3 s^-1].
    """

    n_data = np.asarray(n_data, dtype=float)
    Teq_data = np.asarray(Teq_data, dtype=float)

    valid = (
        np.isfinite(n_data)
        & np.isfinite(Teq_data)
        & (n_data > 0)
        & (Teq_data > 0)
    )

    n_data = n_data[valid]
    Teq_data = Teq_data[valid]

    order = np.argsort(n_data)
    n_data = n_data[order]
    Teq_data = Teq_data[order]

    fill_value = "extrapolate" if extrapolate else np.nan

    logTeq_of_logn = interp1d(
        np.log10(n_data),
        np.log10(Teq_data),
        kind=kind,
        bounds_error=False,
        fill_value=fill_value,
    )

    def Teq_of_n(n):
        n = np.asarray(n, dtype=float)
        return 10.0**logTeq_of_logn(np.log10(n))

    def Gamma_of_n(n):
        n = np.asarray(n, dtype=float)
        T = Teq_of_n(n)
        return n * cool_Lambda(T)

    def Hvol_of_n(n):
        n = np.asarray(n, dtype=float)
        return n * Gamma_of_n(n)

    return Gamma_of_n, Hvol_of_n, Teq_of_n