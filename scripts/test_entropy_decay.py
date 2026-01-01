import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from astropy.cosmology import Planck18
import astropy.units as u

# 1. THE DATA (Clean Audit)
# z: Redshift
# R: Rushing Factor
data_z = np.array([0.0, 0.5, 2.0, 10.0])
data_R = np.array([1.0, 3.17, 4.60, 22.0])
sigma = np.array([0.1, 1.5, 0.5, 5.0]) # Uncertainties

# 2. CONVERT Z TO COSMIC TIME (Age in Gyr)
# We use Planck18 cosmology to get the age of the universe at each z
data_t = Planck18.age(data_z).value # Gyr
print("Redshifts:", data_z)
print("Cosmic Ages (Gyr):", data_t)

# 3. DEFINE MODELS

# Model A: Geometric Power Law (The Old Leviathan)
# R(z) = (1+z)^alpha
def model_geometric(z, alpha):
    return (1 + z)**alpha

# Model B: Thermodynamic Entropy Decay (Your New Hypothesis)
# R(t) = 1 + S_init * exp(-lambda * t)
# We force it to asymptote to 1 at t -> infinity (or t_current)
def model_thermodynamic(t, S_init, lam):
    # We want R=1 at t=13.8 (Now)? Or R approaches 1 asymptotically?
    # Let's try the user's pure decay form: R = 1 + A * exp(-lambda * t)
    return 1 + S_init * np.exp(-lam * t)

# 4. PERFORM FITS

# Fit Geometric (vs Z)
popt_geo, _ = curve_fit(model_geometric, data_z, data_R, sigma=sigma)
alpha_fit = popt_geo[0]

# Fit Thermodynamic (vs Time)
# Initial guess: S=50, lambda=0.5
popt_therm, pcov_therm = curve_fit(model_thermodynamic, data_t, data_R, sigma=sigma, p0=[50, 0.5])
S_fit, lam_fit = popt_therm

# 5. VISUALIZATION
plt.figure(figsize=(12, 6))

# Plot 1: The Geometric View (vs Redshift)
plt.subplot(1, 2, 1)
plt.errorbar(data_z, data_R, yerr=sigma, fmt='ko', label='Audit Data')
z_range = np.linspace(0, 11, 100)
plt.plot(z_range, model_geometric(z_range, alpha_fit), 'b--', linewidth=2, label=fr'Geometric: $(1+z)^{{{alpha_fit:.2f}}}$')
plt.title("Geometric View (Space)")
plt.xlabel("Redshift (z)")
plt.ylabel("Rushing Factor (R)")
plt.grid(True, alpha=0.3)
plt.legend()

# Plot 2: The Thermodynamic View (vs Time)
plt.subplot(1, 2, 2)
plt.errorbar(data_t, data_R, yerr=sigma, fmt='ko', label='Audit Data')
t_range = np.linspace(0, 13.8, 100)
plt.plot(t_range, model_thermodynamic(t_range, S_fit, lam_fit), 'r-', linewidth=2, label=fr'Entropy: $1 + {S_fit:.0f}e^{{-{lam_fit:.2f}t}}$')
plt.title("Thermodynamic View (Time)")
plt.xlabel("Age of Universe (Gyr)")
plt.gca().invert_xaxis() # Time flows right to left (Old -> Now)
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('paper/figures/model_comparison.png')

# 6. GOODNESS OF FIT CHECK
# Calculate Chi-Squared for both
resid_geo = data_R - model_geometric(data_z, alpha_fit)
chi_geo = np.sum((resid_geo / sigma)**2)

resid_therm = data_R - model_thermodynamic(data_t, S_fit, lam_fit)
chi_therm = np.sum((resid_therm / sigma)**2)

print("\n--- MODEL SHOWDOWN ---")
print(f"Geometric Chi-Sq:    {chi_geo:.4f}")
print(f"Thermodynamic Chi-Sq: {chi_therm:.4f}")

if chi_therm < chi_geo:
    print("-> WINNER: THERMODYNAMICS. The universe is decaying exponentially.")
else:
    print("-> WINNER: GEOMETRY. The universe scales with expansion.")
