"""
Null-Test Engine
Generates randomized control datasets (Monte Carlo) to validate significance.
"""

import numpy as np
import healpy as hp
from scipy.stats import ortho_group

class NullGenerator:
    """
    Generates isotropically rotated copies of a CMB map to build a 
    null distribution for geometric tests.
    """
    
    def __init__(self, map_data, seed=None):
        """
        Args:
            map_data (array): The original HEALPix map.
            seed (int): Optional seed for reproducibility.
        """
        self.original_map = map_data
        self.rng = np.random.default_rng(seed)
        
    def _get_random_rotation(self):
        """
        Generates a random 3D rotation matrix (SO(3)).
        Uses scipy.stats.ortho_group to ensure uniform sampling on the sphere.
        """
        # Generate a random 3x3 orthogonal matrix with determinant +1 (Rotation)
        # ortho_group.rvs(3) might return det -1 (Reflection), so we enforce det +1
        R = ortho_group.rvs(3, random_state=self.rng)
        if np.linalg.det(R) < 0:
            R[:, 0] *= -1 # Flip one column to restore det to +1
        return R

    def generate_nulls(self, n_sims=100):
        """
        Yields rotated maps.
        
        Yields:
            (int, array): Index of simulation, Rotated Map array.
        """
        for i in range(n_sims):
            # Get random rotation matrix
            R = self._get_random_rotation()
            
            # Convert matrix to Euler angles (phi, theta, psi) for healpy
            # Note: healpy's 'rot' parameter in rotate_map_pixel is flexible,
            # but using a Rotator object with a matrix is robust.
            r_engine = hp.Rotator(rot=R, deg=True)
            
            # Apply rotation
            # We use rotate_map_pixel which performs interpolation.
            # For exact algebra, rotate_alm is better, but pixel rotation 
            # preserves mask structures better if we add masking later.
            rotated_map = r_engine.rotate_map_pixel(self.original_map)
            
            yield i, rotated_map

import numpy as np
import healpy as hp

def generate_masked_null(real_map, mask, lmax=512):
    """
    Generates a Gaussian Random Field (GRF) constrained by the 
    power spectrum of the real map and the physical mask.
    """
    nside = hp.get_nside(real_map)
    
    # 1. Extract the Power Spectrum (Cl) from the real map
    # We use the masked map to get the observed power
    cls = hp.anafast(real_map * mask, lmax=lmax)
    
    # 2. Correct for the mask bias (f_sky)
    f_sky = np.mean(mask)
    cls_corrected = cls / f_sky
    
    # 3. Synthesize a new random sky from those Cls
    null_map = hp.synfast(cls_corrected, nside, lmax=lmax, verbose=False)
    
    # 4. Apply the SAME mask to the null map
    return null_map * mask
