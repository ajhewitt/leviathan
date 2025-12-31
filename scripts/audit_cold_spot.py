import os
import healpy as hp
import numpy as np
import matplotlib.pyplot as plt
from leviathan.engines import voids
from leviathan.validation import nulling

# --- CONFIG ---
PLANCK_PATH = "data/raw/planck/smica.fits"
# Coordinates for the Eridanus Center
COLD_SPOT_COORDS = (209.3, -57.4) # Galactic Longitude/Latitude
VOID_RADIUS = 5.0 # Degrees

def run_void_audit():
    print("Leviathan Phase III: The Masked Void Audit")
    print("-------------------------------------------")
    
    # 1. Load Real Map and Mask
    print("-> Ingesting Planck SMICA and Galactic Mask...")
    # Map HDU 0, Mask usually in a separate file or specific HDU
    full_map = hp.read_map(PLANCK_PATH, field=0, verbose=False)
    # Generate a simple 20deg Galactic Cut mask if you don't have the official one
    nside = hp.get_nside(full_map)
    mask = np.ones(hp.nside2npix(nside))
    lat_threshold = np.radians(20)
    theta, phi = hp.pix2ang(nside, np.arange(len(mask)))
    mask[np.abs(theta - np.pi/2) < lat_threshold] = 0

    # 2. Measure the Spot in the Real Map
    t_obs, t_std = voids.get_void_profile(full_map * mask, *COLD_SPOT_COORDS, VOID_RADIUS)
    print(f"-> Observed Temp Anomaly: {t_obs*1e6:.2f} uK")

    # 3. Statistical Comparison
    print(f"-> Generating 100 Masked Nulls...")
    null_results = []
    for i in range(100):
        # Use our new masked-aware generator
        n_map = nulling.generate_masked_null(full_map, mask)
        t_null, _ = voids.get_void_profile(n_map, *COLD_SPOT_COORDS, VOID_RADIUS)
        null_results.append(t_null)
        if (i+1) % 20 == 0: print(f"   Progress: {i+1}/100")

    # 4. Results
    mu = np.mean(null_results)
    std = np.std(null_results)
    sig = (t_obs - mu) / std
    
    print("\n--- RESULTS ---")
    print(f"   Significance: {abs(sig):.2f} sigma")
    
    # 5. The Leviathan Curve: Density vs. Temperature
    # In a PbC universe, a void of this temperature implies a density drop 
    # Delta_rho that shouldn't have formed by z=0.5.
    print(f"-> Predicted Void Depth: Delta_rho ~ {abs(sig)*0.15:.2f} (Over-cleared)")

if __name__ == "__main__":
    run_void_audit()
