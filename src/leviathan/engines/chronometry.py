import numpy as np
from scipy.integrate import quad
from astropy.cosmology import Planck18
import astropy.units as u

def get_coord_age(z):
    """
    Returns the standard LambdaCDM Coordinate Age (t) at redshift z in Gyr.
    """
    return Planck18.age(z).value

def get_structural_age(z, alpha=0.0):
    """
    Calculates the 'Structural Age' (tau) based on the Temporal Density Hypothesis.
    
    d_tau = (t_0 / t)^alpha * dt
    
    If alpha=0, returns standard LambdaCDM age.
    If alpha>0, returns the 'dilated' causal age.
    """
    t_coord = Planck18.age(z).value # Gyr
    t_now = Planck18.age(0).value   # Gyr
    
    # The integral of (t0/t)^alpha dt from 0 to t_coord
    # Analytical solution for alpha != 1:
    # tau = (t0^alpha * t^(1-alpha)) / (1-alpha)
    
    if alpha == 1.0:
        # Singularity at alpha=1 (Logarithmic divergence)
        # We handle this closer to the limit, but for code stability:
        return np.inf
    
    term = (t_now**alpha * t_coord**(1 - alpha)) / (1 - alpha)
    return term
