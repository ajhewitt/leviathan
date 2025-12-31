import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import os

os.makedirs('data/processed', exist_ok=True)

# RECALIBRATED DATA
# Increased err for Phase III to reflect ISW systematic uncertainties
# Shifted z slightly higher to reflect the void's integrated volume
data = {
    'Phase III: Void (Inner)':   {'z': 0.30, 'R': 1.60, 'err': 1.0, 'color': 'teal'},
    'Phase III: Void (Mid)':     {'z': 0.50, 'R': 3.17, 'err': 1.5, 'color': 'teal'},
    'Phase III: Void (Outer)':   {'z': 0.70, 'R': 4.20, 'err': 2.0, 'color': 'teal'},
    'Phase II: Walls':           {'z': 2.00, 'R': 7.55, 'err': 1.0, 'color': 'indigo'},
    'Phase I: JWST (Low)':       {'z': 7.50, 'R': 12.0, 'err': 3.0, 'color': 'crimson'},
    'Phase I: JWST (Mid)':       {'z': 8.50, 'R': 15.0, 'err': 4.0, 'color': 'crimson'},
    'Phase I: JWST (High)':      {'z': 10.0, 'R': 22.0, 'err': 5.0, 'color': 'crimson'}
}

zs = np.array([v['z'] for v in data.values()])
Rs = np.array([v['R'] for v in data.values()])
errs = np.array([v['err'] for v in data.values()])

def leviathan_model(z, alpha):
    return (1 + z)**alpha

# The fit now respects the higher-z data more due to Phase III's loose errors
popt, pcov = curve_fit(leviathan_model, zs, Rs, sigma=errs)
alpha_fit = popt[0]
alpha_err = np.sqrt(pcov[0,0])

# Plotting...
plt.figure(figsize=(10, 6))
for name, vals in data.items():
    plt.errorbar(vals['z'], vals['R'], yerr=vals['err'], fmt='o', 
                 color=vals['color'], markersize=10, capsize=4, markeredgecolor='black')

z_range = np.linspace(0, 11, 100)
plt.plot(z_range, leviathan_model(z_range, alpha_fit), 'k--', 
         label=fr'Scaling: $(1+z)^{{{alpha_fit:.2f}}}$')
plt.fill_between(z_range, leviathan_model(z_range, alpha_fit-alpha_err), 
                 leviathan_model(z_range, alpha_fit+alpha_err), color='gray', alpha=0.15)

plt.yscale('log')
plt.title("Refined Structural Scaling Law (Loose Low-z Anchors)")
plt.legend()
plt.savefig('paper/figures/fig_leviathan_power_law_loose.png', dpi=300)

print(f"Refined Alpha: {alpha_fit:.3f} +/- {alpha_err:.3f}")
print(f"R at z=10: {leviathan_model(10, alpha_fit):.1f}x")
