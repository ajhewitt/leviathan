import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

os.makedirs('paper/figures', exist_ok=True)

# 1. THE COMPLETE AUDIT DATA
# Phase IV (Euclid) is now corrected for the z-dependent Null expectation
data = {
    # Phase III: Eridanus Supervoid (Teal)
    'Phase III: Void (Inner)':   {'z': 0.30, 'zerr': 0.15, 'R': 1.60, 'Rerr': 1.0, 'color': 'teal', 'legend': False},
    'Phase III: Void (Mid)':     {'z': 0.50, 'zerr': 0.20, 'R': 3.17, 'Rerr': 1.5, 'color': 'teal', 'legend': True, 'label': 'Phase III: Voids (Volumetric)'},
    'Phase III: Void (Outer)':   {'z': 0.70, 'zerr': 0.25, 'R': 4.20, 'Rerr': 2.0, 'color': 'teal', 'legend': False},
    
    # Phase II: DESI Mega-Walls (Indigo)
    'Phase II: Walls':           {'z': 2.00, 'zerr': 0.05, 'R': 4.60, 'Rerr': 0.5, 'color': 'indigo', 'legend': True, 'label': 'Phase II: DESI Walls'},

    # Phase IV: Euclid Scaffolding (Gold) - THE MISSING LINK
    # Observed: 1463 Mpc | Null: ~150 Mpc (Young Universe)
    'Phase IV: Euclid':          {'z': 4.50, 'zerr': 1.50, 'R': 9.75, 'Rerr': 2.0, 'color': 'gold', 'legend': True, 'label': 'Phase IV: Euclid Scaffolding'},
    
    # Phase I: JWST Impossible Galaxies (Crimson)
    'Phase I: JWST (Low)':       {'z': 7.50, 'zerr': 0.10, 'R': 12.0, 'Rerr': 3.0, 'color': 'crimson', 'legend': False},
    'Phase I: JWST (Mid)':       {'z': 8.50, 'zerr': 0.15, 'R': 15.0, 'Rerr': 4.0, 'color': 'crimson', 'legend': True, 'label': 'Phase I: JWST High-Mass'},
    'Phase I: JWST (High)':      {'z': 10.0, 'zerr': 0.20, 'R': 22.0, 'Rerr': 5.0, 'color': 'crimson', 'legend': False}
}

# Extract arrays
zs = np.array([v['z'] for v in data.values()])
Rs = np.array([v['R'] for v in data.values()])
yerrs = np.array([v['Rerr'] for v in data.values()])

# 2. THE MODEL: Anchored Power Law
def leviathan_anchored(z, alpha):
    return (1 + z)**alpha

popt, pcov = curve_fit(leviathan_anchored, zs, Rs, sigma=yerrs)
alpha_fit = popt[0]
alpha_err = np.sqrt(pcov[0,0])

# 3. VISUALIZATION
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-darkgrid')

# Plot Data Points
for name, vals in data.items():
    label_text = vals['label'] if vals['legend'] else ""
    plt.errorbar(vals['z'], vals['R'], 
                 xerr=vals['zerr'], yerr=vals['Rerr'], 
                 fmt='o', color=vals['color'], 
                 markersize=12 if 'Euclid' in name else 8, # Highlight Discovery
                 capsize=3, markeredgecolor='black', 
                 alpha=0.9, label=label_text)

# Plot Fit
z_range = np.linspace(0, 11, 100)
plt.plot(z_range, leviathan_anchored(z_range, alpha_fit), 'k--', 
         linewidth=2, label=fr'Leviathan Law: $(1+z)^{{{alpha_fit:.2f}}}$')

plt.fill_between(z_range, 
                 leviathan_anchored(z_range, alpha_fit - alpha_err), 
                 leviathan_anchored(z_range, alpha_fit + alpha_err), 
                 color='gray', alpha=0.2, label=r'1$\sigma$ Confidence')

# Anchor
plt.scatter([0], [1], color='black', marker='x', s=100, label='Present Day (Anchor)', zorder=10)

plt.yscale('log')
plt.xlabel(r"Redshift ($z$)", fontsize=12)
plt.ylabel(r"Rushing Factor ($R = \mathcal{O}_{obs} / \mathcal{O}_{null}$)", fontsize=12)
plt.title("Project Leviathan: Grand Unification (z=0 to z=10)", fontsize=14, fontweight='bold')
plt.grid(True, which="both", ls="-", alpha=0.1)
plt.legend(loc='upper left', frameon=True, fontsize=10)

outfile = 'paper/figures/fig_grand_unification.png'
plt.tight_layout()
plt.savefig(outfile, dpi=300)

print(f"Grand Synthesis Complete. Alpha: {alpha_fit:.3f}")
print(f"Plot saved to: {outfile}")
