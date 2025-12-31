"""
Data Ingestion Layer
Handles loading of Planck FITS files and generation of synthetic mock data.
"""

import numpy as np
import healpy as hp
from leviathan import config

def load_map(filepath, field=0):
    """
    Loads a CMB map from a FITS file and standardizes resolution.
    
    Args:
        filepath (str): Path to the .fits file.
        field (int): The FITS column to read (0=I, 1=Q, 2=U). Default 0 (Temperature).
        
    Returns:
        array: HEALPix map standardized to config.NSIDE.
    """
    print(f"Loading map from {filepath}...")
    # Load map (read-only to save memory)
    raw_map = hp.read_map(filepath, field=field, verbose=False)
    
    # Get current resolution
    nside_in = hp.npix2nside(len(raw_map))
    
    # Downgrade if necessary (Pipeline runs at NSIDE=64 for speed/LSS focus)
    if nside_in > config.NSIDE:
        print(f"Downgrading map from NSIDE {nside_in} to {config.NSIDE}...")
        return hp.ud_grade(raw_map, config.NSIDE)
    elif nside_in < config.NSIDE:
        raise ValueError(f"Input map resolution ({nside_in}) is lower than pipeline requirement ({config.NSIDE}).")
        
    return raw_map

def get_mock_map(mode='random'):
    """
    Generates a synthetic CMB map for pipeline testing.
    
    Args:
        mode (str): 'random' for noise, 'signal' to inject a fake Solar alignment.
    """
    npix = hp.nside2npix(config.NSIDE)
    
    if mode == 'random':
        # Standard Gaussian random field
        return np.random.randn(npix)
    
    elif mode == 'signal':
        # Inject a strong Odd-Parity signal aligned with the Solar Pole
        # 1. Create Odd-Parity Alm (l=3, m=0)
        alm_size = hp.Alm.getsize(config.L_MAX)
        alm = np.zeros(alm_size, dtype=np.complex128)
        idx = hp.Alm.getidx(config.L_MAX, 3, 0)
        alm[idx] = 50.0 # Strong signal
        
        # 2. Create Map
        base_map = hp.alm2map(alm, config.NSIDE)
        
        # 3. Rotate to align with Solar Pole
        # We rotate the MAP, which moves the features.
        solar_vec = config.get_solar_vector()
        # Convert vector to angles
        theta, phi = hp.vec2ang(solar_vec)
        
        # Rotator: (phi, theta, psi)
        r = hp.Rotator(rot=[np.degrees(phi), np.degrees(theta)], deg=True, inv=True)
        return r.rotate_map_pixel(base_map)

import numpy as np
from astropy.io import fits
from astropy.cosmology import Planck18
import os
import gc

def load_quasars(filepath):
    """
    Ingests DESI DR1 'zpix' Catalog (11GB) safely.
    Filters for SPECTYPE='QSO' to reduce memory footprint.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Catalog not found: {filepath}")
    
    print(f"Loading DESI Catalog (Memmap): {filepath}...")
    
    # Open in Memmap mode so we don't crash RAM
    with fits.open(filepath, memmap=True) as hdul:
        data = hdul[1].data
        cols = data.columns.names
        
        # 1. Identify Quasars
        print("-> Scanning SPECTYPE column...")
        spectypes = data['SPECTYPE']
        
        # Handle string vs bytes automatically
        try:
            is_qso = (spectypes == 'QSO')
        except FutureWarning:
            # If numpy complains about string comparison
            is_qso = (np.char.strip(spectypes) == 'QSO')

        # Check for ZWARN (use 'ZWARN' or 'ZWARN_RR')
        warn_key = 'ZWARN' if 'ZWARN' in cols else 'ZWARN_RR'
        
        # Create mask: Must be a Quasar, No warnings, and Z > 0
        is_good = (data[warn_key] == 0) & (data['Z'] > 0)
        mask = is_qso & is_good
        
        count = np.sum(mask)
        print(f"-> Found {count} verified Quasars (filtering out stars/galaxies).")
        
        # 2. Load ONLY the target rows
        ra_key  = 'TARGET_RA' if 'TARGET_RA' in cols else 'RA'
        dec_key = 'TARGET_DEC' if 'TARGET_DEC' in cols else 'DEC'
        
        ra = data[ra_key][mask]
        dec = data[dec_key][mask]
        z = data['Z'][mask]
        
        # Cleanup memory immediately
        del spectypes, is_qso, is_good, mask
        gc.collect()

    print("-> Converting to Comoving 3D Coordinates (Planck18)...")
    
    # 3. Spherical -> Cartesian
    r = Planck18.comoving_distance(z).value # Mpc
    
    phi = np.radians(ra)
    theta = np.radians(90.0 - dec)
    
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z_coord = r * np.cos(theta)
    
    positions = np.column_stack((x, y, z_coord))
    return positions, z
