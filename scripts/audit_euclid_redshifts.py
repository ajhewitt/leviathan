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
# The 33MB Physical Parameters Catalog (General Galaxies)
TARGET_KEY = 'q1/catalogs/PHZ_PF_OUTPUT_FOR_L3/102018212/EUC_PHZ_PHYSPARAM__20241119T224622.918962Z_00.00.fits'
LOCAL_PATH = 'data/raw/euclid/EUC_PHZ_PHYSPARAM_TILE102018212.fits'

os.makedirs('data/raw/euclid', exist_ok=True)
os.makedirs('paper/figures', exist_ok=True)

def audit_euclid_redshifts():
    # 2. DOWNLOAD
    if not os.path.exists(LOCAL_PATH):
        print(f"-> Downloading Euclid PHZ Catalog ({33} MB)...")
        s3 = boto3.client('s3', region_name=REGION, config=Config(signature_version=UNSIGNED))
        s3.download_file(BUCKET_NAME, TARGET_KEY, LOCAL_PATH)
        print("-> Download Complete.")
    else:
        print("-> File already exists. Skipping download.")

    # 3. INSPECT WITH ASTROPY
    print("-> Opening PHZ Catalog...")
    dat = Table.read(LOCAL_PATH)
    
    # 4. IDENTIFY REDSHIFT COLUMN
    # In L3 products, this is often 'PHZ_Z' or 'PHZ_PP_MEDIAN_REDSHIFT'
    z_col = None
    candidates = ['PHZ_Z', 'PHZ_PP_MEDIAN_REDSHIFT', 'Z_MEAN', 'Z_BEST']
    
    print(f"-> Searching for redshift column...")
    for col in dat.colnames:
        if col in candidates:
            z_col = col
            break
            
    if z_col:
        print(f"-> Using Redshift Column: {z_col}")
        zs = dat[z_col]
        
        # 5. FILTER & AUDIT
        # Filter 1: Valid Redshifts
        mask = (zs > 0) & (zs < 10) 
        valid_zs = zs[mask]
        
        # Filter 2: The Redshift Desert
        desert_mask = (valid_zs > 3.0) & (valid_zs < 6.0)
        desert_count = np.sum(desert_mask)
        total_count = len(valid_zs)
        
        print(f"\n--- REDSHIFT AUDIT (Tile 102018212) ---")
        print(f"Total Valid Objects: {total_count}")
        print(f"Redshift Desert Candidates (3 < z < 6): {desert_count}")
        print(f"Desert Fraction: {desert_count/total_count*100:.2f}%")
        
        # 6. PLOT
        plt.figure(figsize=(10,6))
        plt.hist(valid_zs, bins=100, color='indigo', alpha=0.7, label='Euclid Q1 Photo-Z')
        
        # Highlight the Desert
        plt.axvspan(3, 6, color='orange', alpha=0.3, label='The Desert (z=3-6)')
        
        # Add "Rushing" Context
        plt.axvline(2.0, color='red', linestyle='--', alpha=0.5, label='Phase II: Wall (z=2)')
        plt.axvline(7.5, color='red', linestyle=':', alpha=0.5, label='Phase I: JWST (z=7+)')
        
        plt.xlabel('Redshift (z)')
        plt.ylabel('Count')
        plt.title(f'Euclid Deep Field South (Tile 102018212)\nGap Analysis: {desert_count} Candidates Found')
        plt.legend()
        plt.grid(True, alpha=0.2)
        
        outfile = 'paper/figures/euclid_q1_redshift_check.png'
        plt.savefig(outfile)
        print(f"-> Histogram saved to {outfile}")
        
    else:
        print("-> WARNING: Could not find Redshift Column.")
        print(f"Columns: {dat.colnames[:20]}")

if __name__ == "__main__":
    audit_euclid_redshifts()
