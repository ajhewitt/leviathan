import numpy as np
from astropy.io import fits
from astropy.cosmology import Planck18
from astropy.coordinates import SkyCoord
from scipy.spatial import cKDTree
import networkx as nx
import astropy.units as u

# 1. LOAD DATA
fits_path = 'data/raw/desi/zpix-main-dark.fits'
print(f"-> Loading DESI Catalog: {fits_path}...")
with fits.open(fits_path, memmap=True) as hdul:
    data = hdul[1].data
    # Filter for Quasars (SPECTYPE='QSO') and Z > 0
    mask = (data['SPECTYPE'] == 'QSO') & (data['Z'] > 0.0)
    qsos = data[mask]

print(f"-> Total Quasars: {len(qsos)}")

# 2. SPLIT HEMISPHERES
# Standard Definition: NGC (North) vs SGC (South) usually split by Galactic Plane
# For RA approximation: NGC is roughly 100 < RA < 300, SGC is the rest
ra = qsos['TARGET_RA']
dec = qsos['TARGET_DEC']
z = qsos['Z']

# Simple RA split for speed (approximate NGC/SGC)
mask_north = (ra > 80) & (ra < 300)
mask_south = ~mask_north

north_set = {'ra': ra[mask_north], 'dec': dec[mask_north], 'z': z[mask_north]}
south_set = {'ra': ra[mask_south], 'dec': dec[mask_south], 'z': z[mask_south]}

print(f"-> North Sample: {len(north_set['ra'])}")
print(f"-> South Sample: {len(south_set['ra'])}")

# 3. ANALYSIS FUNCTION
def analyze_hemisphere(name, sample):
    print(f"\n--- ANALYZING {name} ---")
    
    # Filter for Cosmic Noon (1.5 < z < 2.5)
    z_mask = (sample['z'] > 1.5) & (sample['z'] < 2.5)
    ra_sub = sample['ra'][z_mask]
    dec_sub = sample['dec'][z_mask]
    z_sub = sample['z'][z_mask]
    
    print(f"-> Quasars in Cosmic Noon (1.5 < z < 2.5): {len(z_sub)}")
    if len(z_sub) < 1000:
        print("-> [FAIL] Insufficient data density.")
        return 0, 0

    # Convert to 3D
    print("-> Converting to Cartesian...")
    # Strip units to avoid deg2 errors
    ra_np = np.array(ra_sub)
    dec_np = np.array(dec_sub)
    dist = Planck18.comoving_distance(z_sub).value
    
    c = SkyCoord(ra=ra_np*u.deg, dec=dec_np*u.deg, distance=dist*u.Mpc)
    xyz = np.array([c.cartesian.x.value, c.cartesian.y.value, c.cartesian.z.value]).T
    
    # Friends-of-Friends
    print("-> Running Percolation (Linking Length = 150 Mpc)...")
    tree = cKDTree(xyz)
    pairs = tree.query_pairs(150.0)
    
    G = nx.Graph()
    G.add_nodes_from(range(len(z_sub)))
    G.add_edges_from(pairs)
    
    # Metrics
    if nx.number_of_nodes(G) > 0:
        components = list(nx.connected_components(G))
        largest = max(components, key=len)
        max_nodes = len(largest)
        
        # Calculate Extent (Approximate Diagonal)
        indices = list(largest)
        pts = xyz[indices]
        # Quick bounding box diagonal
        mins = np.min(pts, axis=0)
        maxs = np.max(pts, axis=0)
        extent = np.linalg.norm(maxs - mins)
        
        # Null Baseline (Standard Random) ~ 380 Mpc
        r_factor = extent / 380.0
        
        print(f"-> Largest Cluster: {max_nodes} nodes")
        print(f"-> Physical Extent: {extent:.1f} Mpc")
        print(f"-> Rushing Factor (R): {r_factor:.2f}")
        return max_nodes, r_factor
    else:
        return 0, 0

# 4. EXECUTE & COMPARE
nodes_N, r_N = analyze_hemisphere("NORTH (NGC)", north_set)
nodes_S, r_S = analyze_hemisphere("SOUTH (SGC)", south_set)

print("\n==========================================")
print("       FALSIFICATION REPORT")
print("==========================================")
print(f"NORTH R-Factor: {r_N:.2f}")
print(f"SOUTH R-Factor: {r_S:.2f}")
delta = abs(r_N - r_S)
print(f"Delta: {delta:.2f}")

if r_N > 2.0 and r_S > 2.0 and delta < 1.0:
    print("\n-> VERDICT: ROBUST. The anomaly is global.")
elif (r_N < 1.5) or (r_S < 1.5):
    print("\n-> VERDICT: FALSIFIED. One or both hemispheres show no anomaly.")
else:
    print("\n-> VERDICT: INCONCLUSIVE / LOCALIZED. Large disparity between hemispheres.")
