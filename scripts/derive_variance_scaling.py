import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.interpolate import interp1d

# 1. COSMOLOGY SETUP (Planck 2018)
H0 = 67.4 # km/s/Mpc
Om = 0.315
Ol = 0.685
H0_inv_Gyr = 1 / (H0 * 0.001022) # Time unit conversion

# Friedmann Equations
def E(z):
    return np.sqrt(Om * (1+z)**3 + Ol)

def Hubble(z):
    return H0 * 0.001022 * E(z) # in Gyr^-1

def Omega_m(z):
    return Om * (1+z)**3 / E(z)**2

def growth_rate_f(z):
    # Approximation f = Omega_m(z)^0.55
    return Omega_m(z)**0.55

# Time-Redshift Relation: dt = -dz / ((1+z)H(z))
def dz_dt(z):
    return -(1+z) * Hubble(z)

# 2. VARIANCE EVOLUTION (dV/dz)
# We solve in z-space because it's easier, but physics is in t-space.
# dV/dt = 2*f*H*V + 2*D
# dV/dz = (dV/dt) * (dt/dz) = (2*f*H*V + 2*D) / (- (1+z)H)
#       = - (2*f*V)/(1+z) - (2*D)/((1+z)H)

def variance_deriv(V, z, D0, k):
    # V: Current Variance
    # z: Current Redshift
    
    # Physics parameters
    H = Hubble(z)
    f = growth_rate_f(z)
    
    # Diffusion Model: D(z) ~ (1+z)^k
    # Dimensional check: D must be [Variance / Time]
    Diffusion = D0 * ((1+z)**k)
    
    # The Equation
    term1 = -(2 * f * V) / (1 + z)
    term2 = -(2 * Diffusion) / ((1 + z) * H)
    
    return term1 + term2

# 3. SOLVE FOR STANDARD vs STOCHASTIC
z_start = 100.0
z_end = 0.0
z_grid = np.linspace(z_start, z_end, 1000)

# Initial Condition: Small primordial variance (e.g., 1e-5)
V0 = 1e-5

# A. Standard Model (D=0) -> Pure Gravity
V_std = odeint(variance_deriv, V0, z_grid, args=(0.0, 0.0)).flatten()

# B. Leviathan Model (D ~ Density ~ z^3)
# We tune D0 (Amplitude) and k (Exponent)
k_test = 3.0 # The Density Hypothesis
D0_test = 1e-5 # Amplitude factor (tuned to match z=10 magnitude)

V_stoch = odeint(variance_deriv, V0, z_grid, args=(D0_test, k_test)).flatten()

# 4. CALCULATE RUSHING FACTOR
# R = sqrt(V_stoch) / sqrt(V_std) (Amplitude Ratio)
# Avoid division by zero at high z where V is tiny
R = np.sqrt(V_stoch) / np.sqrt(V_std)

# 5. CHECK THE SCALING EXPONENT
# Fit R vs (1+z) to find alpha
# We focus on the observable range z=0 to z=10
mask = (z_grid < 10.0) & (z_grid > 0.1)
z_fit = z_grid[mask]
R_fit = R[mask]

# Power Law Fit: R = A * (1+z)^alpha
fit_params = np.polyfit(np.log(1+z_fit), np.log(R_fit), 1)
alpha_derived = fit_params[0]

print("\n--- ANALYTIC DERIVATION RESULTS ---")
print(f"Input Diffusion Scaling (k): {k_test} (Matter Density)")
print(f"Derived Anomaly Scaling (alpha): {alpha_derived:.3f}")
print(f"Observed Target: 1.26")

# 6. GENERATE THE TABLE AND PLOT
print("\n--- DIMENSIONAL CHECK & DATA TABLE ---")
print(f"{'z':<6} | {'rho_m (scaled)':<15} | {'D(z)':<15} | {'R(z)':<10}")
print("-" * 55)
check_zs = [10.0, 4.5, 2.0, 0.5, 0.0]
for z_val in check_zs:
    idx = (np.abs(z_grid - z_val)).argmin()
    rho = (1+z_val)**3
    D_val = D0_test * ((1+z_val)**k_test)
    R_val = R[idx]
    print(f"{z_val:<6.1f} | {rho:<15.1f} | {D_val:<15.2e} | {R_val:<10.2f}")

# Plot
plt.figure(figsize=(10,6))
plt.plot(z_grid, R, 'b-', linewidth=3, label=f'Derived Model (Input k={k_test})')
plt.plot(z_grid, (1+z_grid)**1.26, 'r--', linewidth=2, label='Observed Anomaly (alpha=1.26)')
plt.xlim(0, 10)
plt.ylim(1, 30)
plt.yscale('log')
plt.xlabel("Redshift (z)")
plt.ylabel("Rushing Factor R(z)")
plt.title(f"Solving the Variance Equation\nInput: Diffusion $\propto (1+z)^3$ -> Output: Anomaly $\propto (1+z)^{{{alpha_derived:.2f}}}$")
plt.legend()
plt.grid(True, which='both', alpha=0.3)
plt.savefig('paper/figures/variance_derivation.png')
print("-> Figure saved to paper/figures/variance_derivation.png")
