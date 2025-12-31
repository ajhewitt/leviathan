import os
import numpy as np
import matplotlib.pyplot as plt
from leviathan import ingestion
from leviathan.engines import topology

# --- CONFIG ---
# This points to your 11GB DESI file
DATA_PATH = "data/raw/desi/zpix-main-dark.fits"
LINKING_LENGTH = 150  # Mpc (Standard supercluster linking scale)
HORIZON_LIMIT = 1200  # Mpc (The Causality Limit ~ 3.9 Gly)

def run_real_audit():
    print("Leviathan Phase II: The REAL Mega-Structure Audit")
    print("-----------------------------------------------")
    
    # 1. Load Data
    try:
        # This will use the memmap ingestion to handle the 11GB file safely
        positions, redshifts = ingestion.load_quasars(DATA_PATH)
    except FileNotFoundError:
        print(f"[ERROR] Catalog not found at: {DATA_PATH}")
        return

    # Filter for the relevant epoch (Cosmic Noon)
    # This is where the Hercules-Corona Borealis Great Wall lives (z ~ 2)
    print("-> Filtering for Cosmic Noon (1.5 < z < 2.5)...")
    mask = (redshifts > 1.5) & (redshifts < 2.5)
    sample = positions[mask]
    
    print(f"-> Analyzing {len(sample)} quasars in target epoch.")

    # 2. Run Topology Engine
    print(f"-> Building Graph (Linking Length = {LINKING_LENGTH} Mpc)...")
    # This builds the Friends-of-Friends network
    G = topology.build_structure_graph(sample, LINKING_LENGTH)
    
    print("-> Hunting for Giants...")
    size, subgraph = topology.get_largest_structure(G)
    extent = topology.measure_extent(subgraph, sample)
    
    print("\n--- RESULTS ---")
    print(f"   Largest Structure Nodes: {size}")
    print(f"   Physical Extent:         {extent:.1f} Mpc")
    print(f"   Causal Horizon:          {HORIZON_LIMIT} Mpc")
    
    is_violation = extent > HORIZON_LIMIT
    print(f"   Horizon Violation:       {'[YES] - ANOMALY DETECTED' if is_violation else '[NO]'}")
    
    # 3. Visualization
    if is_violation:
        print("\n-> Generating Anomaly Map...")
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot a random subset of background quasars for context (so plot isn't too heavy)
        indices = np.random.choice(len(sample), 5000, replace=False)
        bg = sample[indices]
        ax.scatter(bg[:,0], bg[:,1], bg[:,2], s=1, c='gray', alpha=0.1, label='Background')
        
        # Plot the Monster
        nodes = list(subgraph.nodes())
        monster = sample[nodes]
        ax.scatter(monster[:,0], monster[:,1], monster[:,2], s=10, c='red', label=f'The Anomaly ({extent:.0f} Mpc)')
        
        ax.set_title(f"Horizon Violation Detected\nExtent: {extent:.0f} Mpc (z ~ 2.0)")
        plt.legend()
        
        outfile = "paper/figures/fig_great_wall.png"
        # Ensure directory exists
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        
        plt.savefig(outfile, dpi=300)
        print(f"[SUCCESS] Map saved to {outfile}")

if __name__ == "__main__":
    run_real_audit()
