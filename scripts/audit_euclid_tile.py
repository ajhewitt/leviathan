import boto3
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table
from botocore import UNSIGNED
from botocore.client import Config

# 1. SETUP
BUCKET_NAME = 'nasa-irsa-euclid-q1'
REGION = 'us-east-1'
# The 85MB Science Tile
TARGET_KEY = 'q1/catalogs/MER_FINAL_CATALOG/102018212/EUC_MER_FINAL-CAT_TILE102018212-2F45C0_20241019T073625.426663Z_00.00.fits'
LOCAL_PATH = 'data/raw/euclid/EUC_MER_FINAL-CAT_TILE102018212.fits'

os.makedirs('data/raw/euclid', exist_ok=True)

def audit_euclid_tile():
    # 2. DOWNLOAD
    if not os.path.exists(LOCAL_PATH):
        print(f"-> Downloading Euclid Tile 102018212 ({85} MB)...")
        s3 = boto3.client('s3', region_name=REGION, config=Config(signature_version=UNSIGNED))
        s3.download_file(BUCKET_NAME, TARGET_KEY, LOCAL_PATH)
        print("-> Download Complete.")
    else:
        print("-> File already exists. Skipping download.")

    # 3. INSPECT WITH ASTROPY
    print("-> Opening Catalog...")
    dat = Table.read(LOCAL_PATH)
    
    # 4. CHECK COORDINATES (Identify Field)
    ra_min, ra_max = np.min(dat['RIGHT_ASCENSION']), np.max(dat['RIGHT_ASCENSION'])
    dec_min, dec_max = np.min(dat['DECLINATION']), np.max(dat['DECLINATION'])
    
    print(f"\n--- TILE AUDIT ---")
    print(f"Objects: {len(dat)}")
    print(f"RA Range:  {ra_min:.2f} to {ra_max:.2f}")
    print(f"Dec Range: {dec_min:.2f} to {dec_max:.2f}")
    
    # Check for Fornax (approx RA 53.1, Dec -27.8)
    if 50 < np.mean(dat['RIGHT_ASCENSION']) < 56 and -30 < np.mean(dat['DECLINATION']) < -25:
        print("-> IDENTITY CONFIRMED: Euclid Deep Field Fornax (EDF-F)")
    else:
        print("-> Identity: Unknown/Other (Check coordinates vs EDF definitions)")

    # 5. CHECK REDSHIFT DESERT (z=3-6)
    # Note: Column names vary; looking for Z_PHOT or similar. 
    # Usually 'Z_MEAN' or 'Z_PHOT' in MER catalogs.
    z_col = None
    for col in dat.colnames:
        if 'Z' in col and 'PHOT' in col: 
            z_col = col
            break
            
    if z_col:
        print(f"-> Using Redshift Column: {z_col}")
        zs = dat[z_col]
        # Filter valid redshifts
        mask = (zs > 0) & (zs < 10)
        valid_zs = zs[mask]
        
        desert_count = np.sum((valid_zs > 3.0) & (valid_zs < 6.0))
        print(f"-> 'Redshift Desert' Candidates (3 < z < 6): {desert_count}")
        
        # Plot
        plt.figure(figsize=(10,5))
        plt.hist(valid_zs, bins=100, color='purple', alpha=0.7, label='Euclid Q1 Phot-Z')
        plt.axvspan(3, 6, color='orange', alpha=0.2, label='The Desert (Target Gap)')
        plt.xlabel('Redshift (z)')
        plt.ylabel('Count')
        plt.title(f'Euclid Tile 102018212: Redshift Distribution (N={len(valid_zs)})')
        plt.legend()
        plt.savefig('paper/figures/euclid_q1_redshift_check.png')
        print("-> Histogram saved to paper/figures/euclid_q1_redshift_check.png")
    else:
        print("-> WARNING: Could not auto-detect Photometric Redshift column.")
        print(f"Available columns: {dat.colnames[:10]}...")

if __name__ == "__main__":
    audit_euclid_tile()
