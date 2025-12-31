![Project Leviathan](leviathan_banner.jpg)

**Principal Investigator:** A. Hewitt  
**Status:** ACTIVE (Phase I: Ingestion)  
**Date:** December 30th, 2025

## 1. Project Overview

**Project Leviathan** is a computational investigation into the **Temporal Density Hypothesis**. This framework challenges the standard $\Lambda$CDM assumption that time flows linearly ($d\tau = dt$) back to the Big Bang.

Instead, we posit that the rate of causal processing ($\tau$) scales inversely with the complexity of the Universe, following a power law $\tau \propto t^{-\alpha}$. This implies an **Asymptotic Singularity** where the "first second" of the Universe contained an effectively infinite causal duration, rendering Inflation obsolete and explaining the "impossible" maturity of the early Universe.

The pipeline performs a rigorous **Null-Test Audit** across three cosmological epochs to falsify this hypothesis:
1.  **The High-Z Era:** Testing the "Structural Age" of JWST galaxies vs. Coordinate Time.
2.  **The Cosmic Noon:** Testing for Mega-Structures exceeding the Causal Horizon.
3.  **The CMB Era:** Testing the formation rate of the Eridanus Supervoid (Cold Spot).

## 2. Research Aims (The "Monsters")

We audit anomalies that represent "Causality Breakers" in the standard model.

| Audit | Target Anomaly | Metric | The "Impossible" Factor |
| :--- | :--- | :--- | :--- |
| **A. Chronometry** | JWST Galaxies ($z > 10$) | **Maturity Ratio ($R_m$)** | Galaxies appearing older than the Universe's coordinate age. |
| **B. Connectivity** | Hercules-Corona Wall | **Graph Diameter** | Connected structures larger than the causality horizon ($> 1.2$ Gly). |
| **C. Vacuum** | The Cold Spot | **Void Depth** | Supervoids clearing faster than Dark Energy growth allows. |

---

## 3. Repository Structure

### `/paper` (Research Proposal & Manuscripts)
* `proposal.pdf`: The formal definition of the Temporal Density Hypothesis and Singularity Asymptote.
* `proposal.tex`: LaTeX source.

### `/scripts` (Execution Entry Points)
These scripts run specific scientific audits.

#### **Phase I: The Chronometry Audit (JWST)**
* `audit_early_mass.py`: Ingests JWST/JADES catalogs to plot Stellar Mass vs. Available Time. Fits the $\alpha$ exponent.
* `audit_maturity.py`: Calculates the "Maturity Ratio" for high-z candidates.

#### **Phase II: The Mega-Structure Audit**
* `audit_connectivity.py`: Runs Friends-of-Friends (FoF) clustering on Quasar catalogs to find super-horizon structures.
* `run_null_walls.py`: Generates random point clouds to test the statistical likelihood of 10-Gly walls.

#### **Phase III: The Void Audit**
* `audit_cold_spot.py`: Cross-correlates Planck SMICA maps with galaxy density (WISE) to test void formation rates.

### `/src/leviathan/engines` (Physics Logic)
Core mathematical modules implementing the specific tests.

* `chronometry.py`: Implements the $\tau(t)$ integration and Press-Schechter mass limits.
* `topology.py`: Graph theory algorithms (MST, FoF) for structure detection.
* `voids.py`: Geodesic distance calculators for void/spot alignment.

### `/src/leviathan` (Core)
* `ingestion.py`: Standardized loading for Planck, JWST, and SDSS catalogs.
* `nulling.py`: Generates isotropic Gaussian Random Fields ($C_l$ preserved) for control tests.
* `config.py`: Central repository of Cosmological Parameters ($H_0$, $\Omega_m$, $\alpha$).

---

## 4. Usage

To reproduce the Phase I "Early Bird" audit:

```bash
# 1. Clone the repository
git clone [https://github.com/ajhewitt/leviathan](https://github.com/ajhewitt/leviathan)
cd leviathan

# 2. Run the Chronometry Audit (requires astropy)
python scripts/audit_early_mass.py
```

## 5. Acknowledgments

Data provided by the Planck Collaboration (2018 Release), JWST (MAST Archive), and SDSS/BOSS. Analysis performed using `astropy`, `healpy`, and `scipy`.

## 6. License

MIT
