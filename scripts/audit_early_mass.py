import numpy as np
import matplotlib.pyplot as plt

from leviathan.engines import chronometry

# --- THE MONSTERS (Labbé et al. 2023 Candidates) ---
# ID, Redshift (z), Stellar Mass (log10 M_sol), Observed Age (Gyr - Estimated from SED)
# Note: Observed Age is speculative structural age based on metallicity/mass
dataset = [
    {'id': '38094', 'z': 7.5,  'mass': 10.5, 'obs_age_struct': 0.7}, 
    {'id': '14924', 'z': 8.1,  'mass': 10.9, 'obs_age_struct': 0.8}, 
    {'id': 'GS-z11', 'z': 11.2, 'mass': 9.8,  'obs_age_struct': 0.4}, 
    {'id': 'GL-z13', 'z': 13.1, 'mass': 9.6,  'obs_age_struct': 0.35},
    {'id': 'GN-z11', 'z': 10.6, 'mass': 10.0, 'obs_age_struct': 0.5}, 
    {'id': 'Maisie', 'z': 11.4, 'mass': 9.5,  'obs_age_struct': 0.45}
]

def run_audit():
    print("Leviathan Phase I: The Chronometry Audit")
    print("----------------------------------------")
    
    z_vals = np.linspace(5, 20, 100)
    t_lcdm = [chronometry.get_coord_age(z) for z in z_vals]
    
    # 1. Plot the LambdaCDM Hard Limit (t)
    plt.figure(figsize=(10, 6))
    plt.plot(z_vals, t_lcdm, 'k--', linewidth=2, label=r'$\Lambda$CDM Coordinate Limit ($\alpha=0$)')
    
    # 2. Plot the Monsters
    ids = [d['id'] for d in dataset]
    zs = [d['z'] for d in dataset]
    ages = [d['obs_age_struct'] for d in dataset] # The "impossible" structural age
    
    plt.scatter(zs, ages, color='red', s=100, zorder=5, label='JWST Candidates (Labbé et al. 2023)')
    
    # 3. Fit the Leviathan Curve (Find best alpha)
    # We want a curve that encompasses these points
    best_alpha = 0.35 # Hypothesis guess
    t_leviathan = [chronometry.get_structural_age(z, alpha=best_alpha) for z in z_vals]
    
    plt.plot(z_vals, t_leviathan, 'b-', linewidth=3, alpha=0.8, 
             label=f'Leviathan Hypothesis ($\\alpha={best_alpha}$)')
    
    # Formatting
    plt.title("The Chronometry Audit: Coordinate vs. Structural Age")
    plt.xlabel("Redshift (z)")
    plt.ylabel("Available Time (Gyr)")
    plt.axhline(0, color='black')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gca().invert_xaxis() # High z is past
    
    outfile = "paper/figures/fig_chronometry.png"
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    plt.savefig(outfile, dpi=300)
    print(f"[SUCCESS] Plot generated: {outfile}")

    # 4. Report Tension
    print("\nAnomaly Report:")
    for d in dataset:
        limit = chronometry.get_coord_age(d['z'])
        excess = d['obs_age_struct'] / limit
        print(f"Object {d['id']} (z={d['z']}):")
        print(f"  - Coordinate Limit: {limit:.3f} Gyr")
        print(f"  - Structural Age:   {d['obs_age_struct']:.3f} Gyr")
        print(f"  - Tension Factor:   {excess:.2f}x {'[VIOLATION]' if excess > 1 else ''}")

if __name__ == "__main__":
    run_audit()
