import numpy as np
import matplotlib.pyplot as plt
from leviathan import ingestion
from leviathan.engines import topology
import os

# --- CONFIG ---
DATA_PATH = "data/raw/desi/zpix-main-dark.fits"
# LINKING_STEPS = [70, 90, 110, 130] # Mpc
# Change Line 9 to this lower range:
LINKING_STEPS = [30, 40, 50, 60] # Mpc

def shuffle_universe(positions):
    """
    Creates a null universe by shuffling RA/DEC/Z independently.
    This preserves the n(z) curve but destroys all structure.
    """
    n = len(positions)
    # Convert back to spherical to shuffle properly? 
    # Actually, simpler: just shuffle the X, Y, Z columns independently.
    # This destroys angular correlations.
    x = positions[:,0].copy()
    y = positions[:,1].copy()
    z = positions[:,2].copy()
    np.random.shuffle(x)
    np.random.shuffle(y)
    np.random.shuffle(z)
    return np.column_stack((x, y, z))

def run_sweep():
    print("Leviathan Phase II-B: The Percolation Audit")
    print("-------------------------------------------")
    
    # 1. Load Real Data
    print("-> Loading DESI Catalog...")
    pos_real, z_real = ingestion.load_quasars(DATA_PATH)
    
    # Filter for Cosmic Noon
    mask = (z_real > 1.5) & (z_real < 2.5)
    sample_real = pos_real[mask]
    
    # Downsample for speed if needed (DESI is huge)
    # Let's take a random 10% if it's too slow, but for 700k points, 
    # scipy KDTree is fast enough to do all of them.
    print(f"-> Analyzing {len(sample_real)} quasars (Real).")
    
    # 2. Generate Null Data
    print("-> Generating Randomized Control...")
    sample_null = shuffle_universe(sample_real)

    results_real = []
    results_null = []

    # 3. The Sweep
    print("\nStarting Linking Length Sweep...")
    print(f"{'Link (Mpc)':<15} | {'Real Max (Mpc)':<20} | {'Null Max (Mpc)':<20} | {'Tension'}")
    print("-" * 75)

    for r_link in LINKING_STEPS:
        # Measure Real
        G_real = topology.build_structure_graph(sample_real, r_link)
        sz_real, sub_real = topology.get_largest_structure(G_real)
        ext_real = topology.measure_extent(sub_real, sample_real)
        
        # Measure Null
        G_null = topology.build_structure_graph(sample_null, r_link)
        sz_null, sub_null = topology.get_largest_structure(G_null)
        ext_null = topology.measure_extent(sub_null, sample_null)
        
        # Ratio
        ratio = ext_real / ext_null if ext_null > 0 else 0
        
        print(f"{r_link:<15} | {ext_real:<20.1f} | {ext_null:<20.1f} | {ratio:.1f}x")
        
        results_real.append(ext_real)
        results_null.append(ext_null)

    # 4. Plot
    plt.figure(figsize=(10, 6))
    plt.plot(LINKING_STEPS, results_real, 'ro-', linewidth=2, label='Real Universe (DESI)')
    plt.plot(LINKING_STEPS, results_null, 'k--', linewidth=2, label='Random Noise (Null)')
    
    plt.axhline(1200, color='blue', linestyle=':', label='Causal Horizon (1.2 Gpc)')
    
    plt.xlabel("Linking Length (Mpc)")
    plt.ylabel("Largest Structure Size (Mpc)")
    plt.title("Percolation Threshold: Structure vs. Noise")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    outfile = "paper/figures/fig_percolation.png"
    plt.savefig(outfile, dpi=150)
    print(f"\n[SUCCESS] Sweep plot saved to {outfile}")

if __name__ == "__main__":
    run_sweep()
