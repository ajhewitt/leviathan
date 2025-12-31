import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, join
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.cosmology import Planck18
from scipy.spatial import cKDTree
import networkx as nx
import os

# 1. SETUP
MER_PATH = 'data/raw/euclid/EUC_MER_FINAL-CAT_TILE102018212.fits' # RA/DEC
PHZ_PATH = 'data/raw/euclid/EUC_PHZ_PHYSPARAM_TILE102018212.fits' # Redshifts
OUTPUT_DIR = 'paper/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def audit_connectivity():
    print(f"-> Loading Catalogs...")
    mer = Table.read(MER_PATH)
    phz = Table.read(PHZ_PATH)
    
    # 2. JOIN
    print(f"-> Joining Position (N={len(mer)}) + Redshift (N={len(phz)})...")
    data = join(mer, phz, keys='OBJECT_ID', join_type='inner')
    print(f"-> Joined Catalog: {len(data)} objects.")
    
    # 3. FILTER FOR THE DESERT
    z_col = 'PHZ_PP_MEDIAN_REDSHIFT'
    mask = (data[z_col] > 3.0) & (data[z_col] < 6.0)
    desert = data[mask]
    print(f"-> Desert Candidates (3 < z < 6): {len(desert)}")
    
    if len(desert) < 100:
        print("Not enough candidates for clustering analysis.")
        return

    # 4. CONVERT TO 3D CARTESIAN
    print("-> Converting to 3D Comoving Coordinates...")
    
    # FIX: Use np.array() to strip existing FITS units before applying u.deg
    ra_vals = np.array(desert['RIGHT_ASCENSION'])
    dec_vals = np.array(desert['DECLINATION'])
    z_vals = np.array(desert[z_col])

    coords = SkyCoord(ra=ra_vals*u.deg, 
                      dec=dec_vals*u.deg, 
                      distance=Planck18.comoving_distance(z_vals))
    
    xyz = np.array([coords.cartesian.x.value, 
                    coords.cartesian.y.value, 
                    coords.cartesian.z.value]).T
    
    # 5. RUN FRIENDS-OF-FRIENDS (Clustering)
    # Using 15 Mpc Linking Length to detect "Scaffolding"
    print("-> Running Friends-of-Friends (Linking Length = 15 Mpc)...")
    tree = cKDTree(xyz)
    linking_length = 15.0 
    
    pairs = tree.query_pairs(linking_length)
    
    G = nx.Graph()
    G.add_nodes_from(range(len(desert)))
    G.add_edges_from(pairs)
    
    components = list(nx.connected_components(G))
    largest_cc = max(components, key=len)
    
    print(f"\n--- EUCLID CONNECTIVITY RESULTS (z=3-6) ---")
    print(f"Total Clusters Found: {len(components)}")
    print(f"Largest Structure (Nodes): {len(largest_cc)} galaxies")
    
    # Calculate Physical Extent
    indices = list(largest_cc)
    cluster_xyz = xyz[indices]
    
    from scipy.spatial.distance import pdist
    if len(indices) > 1:
        diameter = np.max(pdist(cluster_xyz))
        print(f"Structure Diameter: {diameter:.2f} Mpc")
    else:
        print("Structure Diameter: N/A (Single Node)")
        diameter = 0

    # 6. VISUALIZATION
    plt.figure(figsize=(10,10))
    plt.style.use('dark_background')
    
    # Project to 2D (X-Y Plane slice)
    plt.scatter(xyz[:,0], xyz[:,1], s=1, c='gray', alpha=0.3, label='Background (Desert)')
    plt.scatter(cluster_xyz[:,0], cluster_xyz[:,1], s=30, c='cyan', label=f'Giant Component ({diameter:.0f} Mpc)')
    
    plt.title(f"Euclid 'Desert' Scaffolding (z=3-6)\nN={len(desert)} | Max Dia: {diameter:.1f} Mpc")
    plt.xlabel("Comoving X [Mpc]")
    plt.ylabel("Comoving Y [Mpc]")
    plt.legend()
    plt.axis('equal')
    
    outfile = f"{OUTPUT_DIR}/euclid_structure_map.png"
    plt.savefig(outfile)
    print(f"-> Map saved to {outfile}")

if __name__ == "__main__":
    audit_connectivity()
