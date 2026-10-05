# Nonlinear Analysis of HRV in Cardiac Patients Using Multiscale Entropy and Compression

This repository contains the source code and experimental pipeline associated with the paper:

> **Nonlinear Analysis of HRV in Cardiac Patients Using Multiscale Entropy and Compression**

submitted to the **26th IEEE International Conference on Bioinformatics and Bioengineering (BIBE 2026)**.

The project investigates nonlinear and complexity-based characteristics of **heart rate variability (HRV)** using RR-interval time series. In particular, it explores **Multiscale Entropy (MSE)** and **compression-based complexity measures** for the analysis and characterization of cardiac dynamics.

---

## Overview

Heart rate variability provides information about the temporal dynamics of cardiac activity. In addition to conventional time- and frequency-domain indices, nonlinear methods can characterize properties related to irregularity, complexity, predictability, and temporal organization of RR-interval sequences.

This work focuses on two complementary approaches:

- **Multiscale Entropy (MSE)** — evaluates the complexity of HRV dynamics across multiple temporal scales.
- **Compression-based analysis** — evaluates the complexity of RR-interval sequences through their compressibility.

The computational pipeline is organized into theses stages:

RR-interval recordings -> Preprocessing -> Nonlinear Analysis -> Feature Extraction -> Statistical Analysis and Evaluation

## Methods

### Multiscale Entropy

Multiscale Entropy evaluates the complexity of a time series at different temporal scales.

For each scale factor, the RR-interval sequence is coarse-grained and an entropy measure is subsequently computed. This allows the analysis to move beyond a single-scale characterization of HRV and investigate how the complexity of cardiac dynamics changes with temporal scale.

Conceptually:

```text
RR intervals
     │
     ├── Scale 1 ──► Entropy
     │
     ├── Scale 2 ──► Entropy
     │
     ├── Scale 3 ──► Entropy
     │
     │      ...
     │
     └── Scale N ──► Entropy
```

The resulting entropy values form a multiscale representation of the RR-interval dynamics.

Multiscale entropy is particularly relevant for HRV because physiological cardiac dynamics are inherently multiscale and cannot always be adequately characterized by a single statistical descriptor.

### Compression-Based Complexity

The repository also implements a compression-based approach to characterize the complexity of RR-interval sequences.

The underlying idea is that the degree to which a sequence can be compressed provides information about its regularity and redundancy. More structured or predictable sequences tend to exhibit greater compressibility, whereas more complex sequences tend to contain less exploitable redundancy.

This provides a complementary perspective to entropy-based measures.

---

## Input Data

The analysis operates on **RR-interval (RRI) time series**.

An RR interval represents the elapsed time between consecutive cardiac beats and is commonly expressed in milliseconds:

```text
RR = [RR₁, RR₂, RR₃, ..., RRₙ]
```

The expected input format and organization should follow the structure used by the preprocessing scripts included in this repository.

> **Note:** The datasets used in this study are not publicly available due to ethical and privacy restrictions. Access may be considered upon reasonable request and subject to institutional approval.


---

## Installation

Clone the repository:

```bash
git clone https://github.com/hrv-ufg/nonlinear-cardiac.git
cd nonlinear-cardiac
```

Create and activate a Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file is not available in the current version of the repository, install the dependencies required by the individual modules under `hrv-analysis/` and `preprocessing/`.

---

## Running the Pipeline

The general workflow is:

### 1. Prepare the RR-interval data

Place the input RR recordings according to the directory structure expected by the preprocessing scripts.

### 2. Run preprocessing

Execute the corresponding preprocessing script:

```bash
python preprocessing/<script>.py
```

### 3. Run HRV analysis

Execute the analysis pipeline:

```bash
python hrv-analysis/src/<script>.py
```

The exact scripts and parameters should be selected according to the experiment being reproduced.

---

## Reproducibility

To reproduce the experiments reported in the paper, the following elements should be kept consistent:

- RR-interval preprocessing;
- input sequence selection;
- windowing strategy, when applicable;
- entropy parameters;
- multiscale configuration;
- compression parameters;
- feature aggregation;
- statistical analysis;
- classification/evaluation protocol, when applicable.

---

## Scientific Context

Nonlinear HRV analysis has been extensively investigated as a way of characterizing the complexity of cardiac dynamics. Entropy-based methods, including Sample Entropy and Multiscale Entropy, are among the commonly investigated approaches for quantifying irregularity and complexity in heart-rate time series.

Compression-based methods provide a complementary perspective by measuring the amount of structure and redundancy that can be exploited in a time series.

The combination of these approaches is investigated in this work to provide a broader characterization of cardiac dynamics.

---

## Relation to the Paper

This repository accompanies the manuscript:

> **Nonlinear Analysis of HRV in Cardiac Patients Using Multiscale Entropy and Compression**

**Conference:**  
26th IEEE International Conference on Bioinformatics and Bioengineering (BIBE 2026)

**Year:** 2026

**Repository:**  
<https://github.com/hrv-ufg/nonlinear-cardiac>

The code is provided to support the reproducibility and further investigation of the computational methods presented in the paper.

---

## License

This project is distributed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [`LICENSE`](LICENSE) file for the complete license terms.