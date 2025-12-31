import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import os

os.makedirs('data/processed', exist_ok=True)

# DATA WITH HORIZONTAL AND VERTICAL ERROR BARS
# xerr represents the redshift depth (z_depth)
data = {
    'Phase III: Void (Inner)':   {'z': 0.30, 'zerr': 0.15, 'R': 1.60, 'Rerr': 1.0, 'color': 'teal'},
    'Phase III: Void (Mid)':     {'z': 0.50, 'zerr': 0.20, 'R': 3.17, 'Rerr': 1.5, 'color': 'teal'},
    'Phase III: Void (Outer)':   {'z': 0.70, 'zerr': 0.25, 'R': 4.20, 'Rerr': 2.0, 'color': 'teal'},
    'Phase II: Walls':           {'z': 2.00, 'zerr': 0.05, 'R': 7.55, 'Rerr': 1.0, 'color': 'indigo'},
    'Phase I: JWST (Low)':       {'z': 7.50, 'zerr': 0.10, 'R': 12.0, 'Rerr': 3.0, 'color': 'crimson'},
    'Phase I: JWST (Mid)':       {'z': 8.50, 'zerr': 0.15, 'R': 15.0, 'Rerr': 4.0, 'color': 'crimson'},
    'Phase I: JWST (High)':      {'z': 10.0, 'zerr': 0.20, 'R': 22.0, 'Rerr': 5.0, 'color': 'crimson'}
}

zs = np.array([v['z'] for v in data.values()])
Rs = np.array([v['R'] for v in data.values()])
yerrs = np.array([v['Rerr'] for v in data.values()])
xerrs = np.array([v['zerr'] for v in data.values()])

def leviathan_model(z, alpha):
    return (1 + z)**alpha

popt, pcov = curve_fit(leviathan_model, zs, Rs, sigma=yerrs)
alpha_fit = popt[0]
alpha_err = np.sqrt(pcov[0,0])

# PLOTTING
plt.figure(figsize=(10, 6))

for name, vals in data.items():
    # Use both xerr and yerr to create the "square" effect
    plt.errorbar(vals['z'], vals['R'], xerr=vals['zerr'], yerr=vals['Rerr'], 
                 fmt='o', color=vals['color'], markersize=8, capsize=3, 
                 markeredgecolor='black', alpha=0.7)

z_range = np.linspace(0, 11, 100)
plt.plot(z_range, leviathan_model(z_range, alpha_fit), 'k--', label=fr'Fit: $(1+z)^{{{alpha_fit:.2f}}}$')
plt.fill_between(z_range, leviathan_model(z_range, alpha_fit-alpha_err), 
                 leviathan_model(z_range, alpha_fit+alpha_err), color='gray', alpha=0.15)

plt.yscale('log')
plt.xlabel(r"Redshift ($z$)")
plt.ylabel(r"Rushing Factor ($R$)")
plt.title("Scaling Law Synthesis with Volumetric Uncertainty")
plt.legend()
plt.savefig('paper/figures/fig_leviathan_scaling_boxes.png', dpi=300)

print(f"Refined Alpha: {alpha_fit:.3f} +/- {alpha_err:.3f}")
