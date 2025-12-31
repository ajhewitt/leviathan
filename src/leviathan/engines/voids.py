import numpy as np
import healpy as hp

def get_void_profile(map_data, lon, lat, radius_deg):
    """
    Extracts the average temperature profile of a suspected void.
    """
    nside = hp.get_nside(map_data)
    vec = hp.ang2vec(lon, lat, lonlat=True)
    
    # Get all pixels within the radius
    pixels = hp.query_disc(nside, vec, np.radians(radius_deg))
    values = map_data[pixels]
    
    return np.mean(values), np.std(values)

def calculate_void_significance(observed_temp, null_mean, null_std):
    """
    Returns the sigma-deviation of the void from Gaussian noise.
    """
    return (observed_temp - null_mean) / null_std
