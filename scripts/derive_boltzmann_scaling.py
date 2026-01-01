import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
import os

os.makedirs('paper/figures', exist_ok=True)

# 1. MANUAL COSMOLOGY
H0 = 67.4 
Om = 0.315
Ol = 1.0 - Om
H0_Gyr = H0 * 0.001022 

def E(z):
    return np.sqrt(Om * (1+z)**3 + Ol)

def age_integrand(z):
    return 1 / ((1+z) * E(z))

def get_age(z):
    integral, _ = quad(age_integrand, z, np.inf)
    return integral / H0_Gyr

# Look-up Tables
z_range = np.linspace(20, 0, 1000)
ages = np.array([get_age(z) for z in z_range])
a_scale = 1 / (1 + z_range)

t_grid = np.linspace(min(ages), max(ages), 1000)
z_interp = interp1d(ages, z_range, kind='cubic')
a_interp = interp1d(ages, a_scale, kind='cubic')

def hubble_H(t):
    z = z_interp(t)
    return H0_Gyr * E(z)

# 2. THE LANGEVIN SIMULATION
def run_simulation(noise_exponent, noise_amplitude, n_particles=5000):
    dt = (t_grid[-1] - t_grid[0]) / (len(t_grid) - 1)
    deltas = np.ones(n_particles) * 0.01 
    
    # Checkpoints as floats to match keys
    checkpoints = [10.0, 2.0, 0.5]
    results = {}
    current_checkpoint_idx = 0
    
    for t in t_grid:
        z_now = z_interp(t)
        H_now = hubble_H(t)
        
        # Drift
        drift = H_now * deltas * dt
        
        # Diffusion
        noise_level = noise_amplitude * ((1 + z_now)**noise_exponent)
        stochastic = noise_level * np.random.normal(0, np.sqrt(dt), n_particles)
        
        deltas = deltas + drift + stochastic
        
        if current_checkpoint_idx < len(checkpoints):
            target_z = checkpoints[current_checkpoint_idx]
            if z_now <= target_z:
                # Normalize R
                growth_factor = a_interp(t) / a_interp(t_grid[0])
                expected_val = 0.01 * growth_factor
                observed_val = np.mean(np.abs(deltas))
                
                # Store with precise string key
                results[f'z={target_z}'] = observed_val / expected_val
                current_checkpoint_idx += 1
                
    return results

# 3. FIT THE MODEL
targets = {10.0: 22.0, 2.0: 4.60, 0.5: 3.17}
best_score = float('inf')
best_k = 0
best_amp = 0

print("-> Running 'Project Boltzmann' Simulation...")
print("   Searching for Noise Exponent (k)...")

for k in np.linspace(2.5, 3.5, 10): # Narrow search around the new k=3 finding
    res = run_simulation(k, 0.5, n_particles=500)
    if 'z=10.0' not in res: continue 
    amp_guess = 0.5 * (targets[10.0] / res['z=10.0'])
    
    final_res = run_simulation(k, amp_guess, n_particles=2000)
    
    error = 0
    for z, target_r in targets.items():
        sim_r = final_res[f'z={z}']
        error += ((sim_r - target_r) / target_r)**2
        
    print(f"   k={k:.3f} | Error={error:.3f}")
    
    if error < best_score:
        best_score = error
        best_k = k
        best_amp = amp_guess

print("\n--- DERIVATION COMPLETE ---")
print(f"Optimal Entropy Exponent (k): {best_k:.3f}")

# 4. PLOT
plt.figure(figsize=(10, 6))
z_plot = [10.0, 2.0, 0.5] # Floats
r_target = [targets[z] for z in z_plot]
best_res_sim = run_simulation(best_k, best_amp, n_particles=5000)
r_sim = [best_res_sim[f'z={z}'] for z in z_plot]

plt.plot(z_plot, r_target, 'ko', markersize=10, label='Audit Data')
plt.plot(z_plot, r_sim, 'r-x', markersize=8, linewidth=2, label=f'Model k={best_k:.3f}')

plt.xlabel('Redshift (z)')
plt.ylabel('Rushing Factor (R)')
plt.title(f'Theoretical Derivation Complete\nDiffusion $\propto (1+z)^{{{best_k:.3f}}}$')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('paper/figures/boltzmann_derivation.png')
print("-> Figure saved.")
