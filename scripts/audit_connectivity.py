import numpy as np
import matplotlib.pyplot as plt

from leviathan.engines import topology

# --- CONFIG ---
UNIVERSE_SIZE = 4000  # Mpc (A box 4 billion light years wide)
NUM_QUASARS = 5000
LINKING_LENGTH = 150  # Mpc (Typical supercluster linking scale)
HORIZON_LIMIT = 1200  # Mpc (The Causality Limit ~ 3.9 Gly)

def generate_random_universe(n, size):
    return np.random.rand(n, 3) * size

def inject_great_wall(positions, length=2000):
    """
    Injects a 'Great Wall' filament that violates the horizon.
    length: Mpc
    """
    # Create a line of quasars
    n_wall = 200
    t = np.linspace(0, 1, n_wall)
    wall_x = t * length + 1000
    wall_y = np.ones_like(t) * 2000 + np.random.normal(0, 20, n_wall) # Thin filament
    wall_z = np.ones_like(t) * 2000 + np.random.normal(0, 20, n_wall)
    
    wall = np.column_stack((wall_x, wall_y, wall_z))
    return np.vstack((positions, wall))

def run_audit():
    print("Leviathan Phase II: The Mega-Structure Audit")
    print("------------------------------------------")
    
    # 1. Null Test (Random Universe)
    print("-> Generating Null Universe (LambdaCDM)...")
    univ_null = generate_random_universe(NUM_QUASARS, UNIVERSE_SIZE)
    G_null = topology.build_structure_graph(univ_null, LINKING_LENGTH)
    size_null, sub_null = topology.get_largest_structure(G_null)
    extent_null = topology.measure_extent(sub_null, univ_null)
    
    print(f"   Largest Structure: {size_null} galaxies")
    print(f"   Physical Extent:   {extent_null:.1f} Mpc")
    print(f"   Horizon Violation: {'YES' if extent_null > HORIZON_LIMIT else 'NO'}")

    # 2. Injection Test (Leviathan Universe)
    print("\n-> Injecting 'Impossible' Wall (2000 Mpc)...")
    univ_lev = inject_great_wall(univ_null, length=2000)
    G_lev = topology.build_structure_graph(univ_lev, LINKING_LENGTH)
    size_lev, sub_lev = topology.get_largest_structure(G_lev)
    extent_lev = topology.measure_extent(sub_lev, univ_lev)
    
    print(f"   Largest Structure: {size_lev} galaxies")
    print(f"   Physical Extent:   {extent_lev:.1f} Mpc")
    print(f"   Horizon Violation: {'YES' if extent_lev > HORIZON_LIMIT else 'NO'}")

    # 3. Plot Comparison
    fig = plt.figure(figsize=(10, 5))
    
    # Plot Null
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.scatter(univ_null[:,0], univ_null[:,1], univ_null[:,2], s=1, alpha=0.3, c='gray')
    # Highlight largest cluster
    if size_null > 0:
        nodes = list(sub_null.nodes())
        cluster = univ_null[nodes]
        ax1.scatter(cluster[:,0], cluster[:,1], cluster[:,2], s=5, c='blue', label='Max Cluster')
    ax1.set_title(f"Null Universe\nMax Extent: {extent_null:.0f} Mpc")
    ax1.set_xlim(0, UNIVERSE_SIZE); ax1.set_ylim(0, UNIVERSE_SIZE); ax1.set_zlim(0, UNIVERSE_SIZE)
    
    # Plot Leviathan
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.scatter(univ_lev[:,0], univ_lev[:,1], univ_lev[:,2], s=1, alpha=0.3, c='gray')
    # Highlight largest cluster
    if size_lev > 0:
        nodes = list(sub_lev.nodes())
        cluster = univ_lev[nodes]
        ax2.scatter(cluster[:,0], cluster[:,1], cluster[:,2], s=10, c='red', label='Injected Wall')
    ax2.set_title(f"Leviathan Universe\nMax Extent: {extent_lev:.0f} Mpc")
    ax2.set_xlim(0, UNIVERSE_SIZE); ax2.set_ylim(0, UNIVERSE_SIZE); ax2.set_zlim(0, UNIVERSE_SIZE)

    outfile = "paper/figures/fig_connectivity.png"
    plt.savefig(outfile, dpi=150)
    print(f"\n[SUCCESS] Visual proof generated: {outfile}")

if __name__ == "__main__":
    run_audit()
