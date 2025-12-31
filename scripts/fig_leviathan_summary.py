import matplotlib.pyplot as plt
import numpy as np

def generate_summary_plot():
    print("Generating Leviathan Synthesis Figure...")
    
    # 1. Data Points from your Audits
    # Phase I: JWST Mass Tension (approximate mass vs z)
    z_i = [7.5, 8.5, 10.0]
    tension_i = [2.5, 3.1, 4.2] # Sigma values from mass audit
    
    # Phase II: DESI Mega-Wall (at Cosmic Noon)
    z_ii = [2.0]
    tension_ii = [7.6] # 7.6x Tension found at 40Mpc
    
    # Phase III: Planck Void (Cold Spot)
    z_iii = [0.22] # Effective redshift of Eridanus void
    tension_iii = [3.17] # Sigma significance from your last run
    
    # 2. Plotting
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Plot Tension vs Redshift
    plt.scatter(z_i, tension_i, color='crimson', s=150, label='Phase I: JWST Early Mass', marker='^', edgecolors='black')
    plt.scatter(z_ii, tension_ii, color='indigo', s=200, label='Phase II: DESI Mega-Walls', marker='s', edgecolors='black')
    plt.scatter(z_iii, tension_iii, color='teal', s=180, label='Phase III: Planck Supervoids', marker='o', edgecolors='black')
    
    # Threshold Lines
    plt.axhline(3, color='orange', linestyle='--', alpha=0.6, label='3σ (Scientific Anomaly)')
    plt.axhline(5, color='red', linestyle='-', alpha=0.4, label='5σ (Discovery Threshold)')
    
    # Formatting
    plt.xlim(11, -0.5) # Time flows right to left (z=11 to 0)
    plt.ylim(0, 10)
    plt.xlabel("Redshift ($z$) — Moving toward Present Day →", fontsize=12)
    plt.ylabel("Observed Tension ($\sigma$)", fontsize=12)
    plt.title("PROJECT LEVIATHAN: Structural Chronometry Audit", fontsize=14, fontweight='bold')
    
    # Add an arrow indicating "The Rushed Universe"
    plt.annotate('Structural Growth "Rushing"', xy=(5, 8), xytext=(8, 9),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=11, fontweight='bold')

    plt.legend(loc='upper left', frameon=True)
    
    # Save results
    outfile = "paper/figures/fig_leviathan_synthesis.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    print(f"[SUCCESS] Final synthesis saved to {outfile}")

if __name__ == "__main__":
    generate_summary_plot()
