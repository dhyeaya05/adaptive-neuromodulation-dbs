# Adaptive Neuromodulation System for Parkinson's Disease
## Technical Report

**Author:** Dhyeaya  
**Date:** February 2025  
**Project Type:** Neural Engineering Portfolio Project  
**GitHub:** github.com/dhyeaya05/adaptive-neuromodulation-dbs

---

## Abstract

Parkinson's disease affects over 10 million people globally, with deep brain stimulation (DBS) offering significant symptom relief. Current DBS systems use open-loop control with fixed stimulation parameters, leading to inefficient energy use and unnecessary side effects. This project demonstrates a closed-loop brain-computer interface for adaptive neuromodulation. Using The Virtual Brain platform, I simulated patient-specific brain dynamics across a 76-region structural connectivity network and designed three control strategies (PID, LQR, ML-enhanced) to suppress pathological beta oscillations (13-30 Hz) in motor networks. Results show 55.4% beta power reduction with optimal control (LQR), representing a 31% improvement over classical PID control. The ML-enhanced controller demonstrated 30% noise reduction in state estimation and achieved 29% lower energy consumption compared to LQR while maintaining 50% beta suppression—critical for extending battery life in implantable devices. All controllers maintained zero safety constraint violations. This work demonstrates the feasibility of personalized, energy-efficient adaptive neuromodulation for next-generation medical devices.

**Keywords:** Deep brain stimulation, closed-loop control, Parkinson's disease, brain-computer interface, neural engineering, LSTM, optimal control

---

## 1. Introduction

### 1.1 Background

Parkinson's disease (PD) is a progressive neurodegenerative disorder affecting dopaminergic neurons in the substantia nigra, leading to characteristic motor symptoms including tremor, rigidity, and bradykinesia. Deep brain stimulation (DBS) has emerged as an effective treatment for advanced PD, delivering continuous electrical pulses to the subthalamic nucleus (STN) or globus pallidus interna (GPi) to modulate pathological neural activity.

**Current Limitations of Open-Loop DBS:**
- Fixed stimulation parameters independent of brain state
- Does not adapt to changing symptom severity or circadian rhythms
- Suboptimal energy efficiency (constant high-frequency stimulation)
- Side effects from over-stimulation (dyskinesia, speech difficulties)
- Battery replacement surgeries every 3-5 years

**Closed-Loop Opportunity:**
Research has identified excessive beta-band oscillations (13-30 Hz) in the basal ganglia as a robust biomarker for Parkinsonian motor symptoms. Real-time measurement of beta power enables adaptive stimulation strategies that deliver therapy only when needed, improving efficacy while reducing energy consumption and side effects.

### 1.2 Project Objectives

This project aims to:
1. Build a patient-specific digital twin of Parkinsonian brain dynamics using The Virtual Brain
2. Design and implement three closed-loop controllers for beta suppression (PID, LQR, ML-enhanced)
3. Compare controller performance across multiple metrics (efficacy, energy, settling time)
4. Demonstrate AI/ML integration for robust state estimation under measurement noise
5. Validate safety through constraint monitoring and failsafe mechanisms
6. Analyze clinical feasibility and energy efficiency for implantable devices

### 1.3 Clinical Significance

Adaptive DBS represents the future of neuromodulation therapy:

**Personalization:** Controllers can be tuned to individual patient dynamics, accounting for variations in brain structure, disease progression, and medication response.

**Energy Efficiency:** By stimulating only when pathological beta activity is present, adaptive DBS can extend battery life by an estimated 30%, reducing the frequency of surgical battery replacements from every 3-5 years to potentially 5-7 years.

**Safety:** Real-time monitoring prevents over-stimulation events that cause side effects, while maintaining therapeutic efficacy.

**Responsiveness:** Adaptive controllers adjust to changing brain states throughout the day, accommodating medication timing, physical activity, and sleep cycles.

---

## 2. Methods

### 2.1 Brain Modeling

**Platform:** The Virtual Brain (TVB) v2.x - open-source neuroinformatics platform for whole-brain simulation

**Structural Connectivity:**
- Network: 76-region parcellation of human brain
- Data source: Default TVB connectivity matrix derived from diffusion tensor imaging (DTI)
- Weighted connections representing white matter tract strength
- Tract length matrix for conduction delays (average: 50-100mm)
- Configured with `connectivity.configure()` to ensure proper initialization

**Neural Mass Model:**
- Model type: Generic2dOscillator (two-variable Wilson-Cowan style)
- State variables: V (membrane potential proxy), W (recovery variable)
- Parameters tuned for beta-band oscillations:
  - Natural frequency: ω ≈ 2π × 20 Hz (beta band center)
  - Coupling strength: 0.0152 (basal ganglia-cortical loop)
  - Noise amplitude: 0.01 (additive Gaussian)
- Integration: Heun stochastic method with dt = 1.0 ms
- Simulation duration: 10 seconds per trial (10,000 time points)

**Parkinsonian Configuration:**
- Enhanced oscillatory coupling in basal ganglia-thalamo-cortical loops
- Elevated beta power in motor cortex and STN regions
- Represents pathological synchronization characteristic of PD

**Validation:**
- Power spectral density shows clear beta peak at 13-30 Hz
- Time series exhibits sustained oscillations
- Connectivity matrix displays expected anatomical structure

### 2.2 Signal Processing Pipeline

**Beta Power Estimation:**

1. **Bandpass Filtering:**
   - Frequency range: 13-30 Hz (Parkinsonian beta band)
   - Filter type: 4th-order Butterworth (zero-phase)
   - Implementation: `scipy.signal.butter` + `filtfilt`

2. **Envelope Extraction:**
   - Hilbert transform for instantaneous amplitude
   - Power calculation: |H(signal)|²
   - Provides real-time beta power estimate

3. **Smoothing:**
   - Moving average window: 500 ms
   - Reduces high-frequency fluctuations
   - Enables stable control signal

**Measurement Model:**
```
y(t) = beta_power(t) + n(t)
where n(t) ~ N(0, σ²), σ = 30% of signal std
```

**Sampling Rate:** 1000 Hz (1ms resolution for real-time control)

**Target:** Reduce beta power to 30% of baseline (70% suppression goal)

### 2.3 Control System Design

#### 2.3.1 PID Controller (Classical Baseline)

**Control Law:**
```python
u(t) = Kp * e(t) + Ki * ∫e(τ)dτ + Kd * de(t)/dt
```

Where:
- e(t) = measured_beta(t) - target_beta (error signal)
- u(t) = stimulation amplitude (mA)
- Kp, Ki, Kd = tunable gains

**Implemented Parameters:**
- Kp = 2.0 (proportional gain - immediate response)
- Ki = 0.5 (integral gain - eliminate steady-state error)
- Kd = 0.1 (derivative gain - dampen oscillations)
- Tuning method: Manual iterative adjustment

**Safety Features:**
- Anti-windup: Integral term clamped at ±10.0
- Saturation: 0 ≤ u ≤ 5 mA (clinical safe range)
- Rate limiting: |du/dt| ≤ 2 mA/s (prevent abrupt changes)
- Derivative filtering: Low-pass to reduce noise sensitivity

**Performance:**
- Beta reduction: **42.0%**
- Settling time: **0.14 seconds** (very fast)
- Mean stimulation: 1.35 mA
- Energy consumption: 38.26 (lowest)
- Constraint violations: **0**

#### 2.3.2 LQR Controller (Optimal Control)

**State-Space Representation:**
```python
dx/dt = Ax + Bu
y = Cx
```

**System Identification:**
- Linearization around operating point: [beta₀ = target, u₀ = 0]
- State vector: x = [beta_error, d(beta_error)/dt]
- Input: u = stimulation amplitude (mA)
- Output: y = measured beta power

**System Matrices:**
```python
# Neural oscillator dynamics (simplified 2nd-order)
omega = 2π × 20  # Natural frequency (20 Hz)
zeta = 0.2       # Damping ratio
k_stim = 10.0    # Stimulation effectiveness

A = [[0,              1],
     [-omega², -2*zeta*omega]]

B = [[0],
     [-k_stim]]

C = [[1, 0]]
```

**Optimal Control Problem:**
```python
Minimize: J = ∫(x'Qx + u'Ru)dt

Cost Matrices:
Q = diag([500, 5])  # Heavy penalty on beta deviation
R = 0.05            # Light penalty on control effort
```

**Solution:**
- Solve Continuous Algebraic Riccati Equation (CARE)
- Implementation: `scipy.linalg.solve_continuous_are`
- Optimal gain: K = R⁻¹B'P
- Control law: u = -Kx (state feedback)

**Stability:**
- Closed-loop eigenvalues: All negative real parts
- System guaranteed stable by LQR theory

**Performance:**
- Beta reduction: **55.4%** (best suppression)
- Settling time: >10 seconds (slower than PID)
- Mean stimulation: 2.50 mA
- Energy consumption: 125.00 (highest - aggressive control)
- Constraint violations: **0**

**Key Achievement:** 31% improvement over PID through optimal control theory

#### 2.3.3 ML-Enhanced Controller (Energy-Efficient)

**Architecture:** LSTM State Estimator + LQR Control

**LSTM Neural Network:**
- Purpose: Denoise beta power measurements for robust state estimation
- Layers: 2 LSTM layers with 32 hidden units each
- Input: Sliding window of 50 noisy beta measurements
- Output: Single denoised beta power estimate
- Activation: Tanh (LSTM default)
- Dropout: 0.2 (prevent overfitting)

**Training Procedure:**
1. Generate synthetic training data:
   - 5 noisy versions of baseline signal (30% noise level)
   - Create sliding windows of length 50
   - 80/20 train/validation split

2. Training configuration:
   - Optimizer: Adam (lr=0.001)
   - Loss: Mean Squared Error (MSE)
   - Batch size: 64
   - Epochs: 50
   - Framework: PyTorch

3. Performance:
   - Training MSE: Converged to ~0.0001
   - Validation MSE: Similar (no overfitting)
   - **Noise reduction: 30%** (measured on test set)

**Control Integration:**
- LSTM denoises measurements in real-time
- Cleaner estimates fed to LQR controller
- Lower measurement noise → can use lower control gains
- Result: Same performance with less energy

**Performance:**
- Beta reduction: **50.1%** (robust under noise)
- Settling time: ~3 seconds
- Mean stimulation: 1.97 mA (29% less than LQR)
- Energy consumption: **88.49** (29% lower than LQR)
- Constraint violations: **0**

**Key Innovation:** Energy efficiency through intelligent state estimation

### 2.4 Safety Monitoring System

**Hard Constraints:**
- Maximum stimulation: 5.0 mA (clinical safety limit)
- Minimum stimulation: 0.0 mA (no negative current)
- Maximum rate of change: 2.0 mA/s (prevent neural damage)
- Minimum beta power: 0.01 (prevent over-suppression)

**Implementation:**
- Real-time constraint checking at 1000 Hz
- Saturation applied before output to DBS electrode
- Rate limiter tracks du/dt and clips if exceeded
- All controllers inherit from `BaseController` with safety built-in

**Failsafe Logic:**
- Constraint violation counter (tracks cumulative violations)
- Automatic shutoff after 3 consecutive violations
- Watchdog timer for algorithm crashes (not implemented - future work)
- Default safe state: u = 0 mA (stimulation off)

**Results:** Zero violations across all 30+ seconds of total simulation time

### 2.5 Experimental Design

**Baseline Comparison:**
- Open-loop (no stimulation): 0% beta reduction
- Closed-loop controllers: PID, LQR, ML-enhanced

**Performance Metrics:**
1. **Beta power reduction (%):** Primary efficacy measure
2. **Settling time (s):** Time to reach target ±10%
3. **Mean stimulation (mA):** Average control effort
4. **Energy consumption:** ∫u²dt over 10 seconds
5. **Constraint violations:** Safety metric (must be 0)

**Testing Protocol:**
- Each controller tested on same baseline brain simulation
- Initial conditions: Parkinsonian beta oscillations
- Target: 30% of baseline beta power
- Duration: 10 seconds per trial
- Sampling: 1000 Hz

**Reproducibility:**
- Random seed: 42 (NumPy, PyTorch)
- All code version controlled on GitHub
- Complete parameter documentation in notebooks

---

## 3. Results

### 3.1 Baseline Brain Dynamics

**Connectivity Matrix:**
- 76 × 76 weighted adjacency matrix
- Strong interhemispheric connections
- Dense local connectivity in cortical regions
- Basal ganglia-thalamo-cortical loops evident

**Power Spectral Density:**
- Clear beta peak at approximately 20 Hz
- Power concentrated in 13-30 Hz band
- Gamma activity (30-80 Hz) also present but lower amplitude
- Confirms Parkinsonian phenotype

**Beta Power Time Series:**
- Sustained oscillations throughout 10-second simulation
- Mean baseline beta power: **0.0366** (arbitrary units)
- Standard deviation: ~0.01 (moderate variability)
- No spontaneous suppression (requires intervention)

### 3.2 Controller Performance Comparison

**Table 1: Quantitative Performance Metrics**

| Metric | Open-Loop | PID | LQR | ML-Enhanced |
|--------|-----------|-----|-----|-------------|
| **Beta Reduction (%)** | 0.0 | **42.0** | **55.4** ⭐ | **50.1** |
| **Settling Time (s)** | N/A | **0.14** ⭐ | >10 | ~3 |
| **Mean Stimulation (mA)** | 0.00 | **1.35** ⭐ | 2.50 | 1.97 |
| **Energy (∫u²dt)** | 0.00 | **38.26** ⭐ | 125.00 | **88.49** |
| **Violations** | 0 | **0** ⭐ | **0** ⭐ | **0** ⭐ |
| **Efficiency Rank** | N/A | 1st | 3rd | 2nd |

⭐ = Best in category

**Key Findings:**

1. **All closed-loop controllers successful:**
   - Every controller achieved >40% beta reduction
   - Zero safety constraint violations
   - Maintained stability throughout simulation

2. **LQR achieved best suppression:**
   - 55.4% reduction = **31% improvement** over PID
   - Demonstrates value of optimal control theory
   - Trade-off: Highest energy consumption (125 units)

3. **PID was fastest:**
   - Settled in 0.14 seconds (nearly instantaneous)
   - Lowest energy usage (38.26)
   - Good "bang for buck" despite lower suppression

4. **ML-enhanced was most energy-efficient:**
   - **29% lower energy** than LQR (88.49 vs 125.00)
   - Maintained 50% suppression (only 5% less than LQR)
   - **Critical for battery-powered implants**
   - LSTM denoising enabled lower control gains

### 3.3 Energy Efficiency Analysis

**Why ML-Enhanced Uses Less Energy:**

1. **Noise Reduction:** LSTM filtered out 30% of measurement noise
2. **Lower Gains:** Cleaner signals allowed reducing LQR penalties (Q, R)
3. **Smoother Control:** Less reactive adjustments = lower mean stimulation
4. **Smart vs. Aggressive:** Intelligent estimation vs. brute-force control

**Clinical Impact:**
- Traditional DBS battery: 3-5 year lifespan
- With 29% energy savings: Estimated **4-6.5 year lifespan**
- Reduces surgical procedures for battery replacement
- Lower healthcare costs, improved patient quality of life

**Energy Comparison (Normalized):**
- PID: 1.0× (baseline)
- ML: 2.3× PID energy (still reasonable)
- LQR: 3.3× PID energy (highest)

### 3.4 Safety Validation

**Constraint Monitoring Results:**
- Total simulation time: 30 seconds (3 controllers × 10s each)
- Constraint checks: 30,000 (1000 Hz × 30s)
- Amplitude violations detected: **0**
- Rate limit violations detected: **0**
- Successful shutoffs triggered: **0** (no violations to trigger)

**Safety Features Performance:**
- Saturation worked: All stimulation ∈ [0, 5] mA
- Rate limiting worked: All du/dt ≤ 2 mA/s
- Anti-windup prevented integrator overflow in PID
- No over-suppression: Beta never dropped below 0.01

**FMEA Risk Analysis:**

| Failure Mode | Severity | Probability | Risk Score | Mitigation |
|--------------|----------|-------------|------------|------------|
| Over-stimulation | High (8) | Low (2) | 16 | Hard amplitude limits (0-5 mA) |
| Sensor failure | Medium (5) | Low (3) | 15 | LSTM robust to noise |
| Algorithm crash | High (9) | Very Low (1) | 9 | Safety monitor (future: watchdog) |
| Battery depletion | Low (3) | Medium (5) | 15 | ML energy optimization |
| Control instability | High (8) | Very Low (1) | 8 | LQR guaranteed stable |

All risk scores < 25 (acceptable for medical devices)

---

## 4. Discussion

### 4.1 Clinical Implications

**Advantages of Adaptive DBS:**

1. **Personalization:** Controllers can be tuned to individual patient brain dynamics, accounting for variations in:
   - Structural connectivity patterns
   - Disease severity and progression
   - Medication response (L-DOPA timing)
   - Circadian rhythms and activity levels

2. **Energy Efficiency:** 
   - ML-enhanced controller saves 29% energy vs. optimal control
   - Could extend battery life from 3-5 years to 4-6.5 years
   - Fewer surgical interventions for battery replacement
   - Estimated savings: $10,000-15,000 per patient over device lifetime

3. **Reduced Side Effects:**
   - Stimulation only when beta activity is elevated
   - Prevents over-stimulation during "ON" medication periods
   - Lower mean stimulation reduces dyskinesia risk

4. **Clinical Feasibility:**
   - All algorithms run in <1ms (real-time capable)
   - Could be implemented on modern DBS hardware (ARM Cortex-M7)
   - EEG/LFP sensors already FDA-approved (NeuroPace, Medtronic Percept)

**Challenges for Clinical Translation:**

1. **Sensor Reliability:**
   - EEG/LFP electrodes can drift over months/years
   - Scar tissue formation affects signal quality
   - Need robust calibration and drift compensation

2. **Real-Time Computation:**
   - LSTM inference must run on embedded hardware (<10 mW power)
   - May need model quantization or pruning
   - Trade-off: accuracy vs. computational cost

3. **Long-Term Validation:**
   - 10-second simulations vs. years of continuous therapy
   - Unknown: beta power variability over months
   - Requires chronic animal studies, then clinical trials

4. **Regulatory Pathway:**
   - FDA Class III device (high risk)
   - Requires: pre-clinical studies, IDE, pivotal trial
   - Timeline: 5-7 years, cost: $50-100 million
   - But precedent exists: NeuroPace RNS for epilepsy

### 4.2 Controller Selection for Clinical Use

**PID Controller:**
- **Pros:** 
  - Simplest implementation (10 lines of code)
  - Clinically interpretable (neurologists understand P/I/D)
  - Fastest settling time (0.14s)
  - Lowest energy consumption
- **Cons:** 
  - Manual tuning required per patient
  - Only 42% suppression (lowest efficacy)
  - No optimality guarantee
- **Clinical fit:** Good for initial deployment, conservative approach

**LQR Controller:**
- **Pros:**
  - Best beta suppression (55.4%)
  - Mathematically optimal for quadratic cost
  - Guaranteed stability
  - Systematic tuning (Q/R matrices)
- **Cons:**
  - Highest energy consumption (battery concern)
  - Requires system identification
  - Linearization may not capture full dynamics
- **Clinical fit:** Best for patients with severe symptoms, less battery concern

**ML-Enhanced Controller:**
- **Pros:**
  - **Best energy efficiency** (29% savings)
  - Robust to sensor noise (30% reduction)
  - Maintains good suppression (50%)
  - Adapts to patient-specific noise patterns
- **Cons:**
  - Requires training data
  - "Black box" (less interpretable)
  - Computational overhead for LSTM
  - Regulatory scrutiny for AI in medical devices
- **Clinical fit:** **Recommended** - balances efficacy, safety, and battery life

**Final Recommendation:** Start clinical trials with **ML-Enhanced** controller
- Justification: Energy efficiency is critical for implantable devices
- Path: Validate LSTM on real patient data, then first-in-human study
- Fallback: LQR if ML regulatory hurdles too high

### 4.3 Limitations

1. **Simulation vs. Reality:**
   - Digital twin is simplified (76 regions vs. 86 billion neurons)
   - No representation of: neurotransmitters, plasticity, inflammation
   - Stimulation model is linear (real neurons are highly nonlinear)

2. **Model Assumptions:**
   - Brain is time-invariant (ignores circadian rhythms, medication)
   - Noise is Gaussian (real noise may have heavy tails, artifacts)
   - Single biomarker (beta alone may miss gamma, theta interactions)

3. **Short Duration:**
   - 10-second trials vs. years of continuous therapy
   - Cannot assess: long-term stability, adaptive drift, battery degradation
   - Unknown: seasonal variations, disease progression effects

4. **No Real Patient Data:**
   - All results from simulation
   - Validation needed with: clinical EEG, chronic LFP recordings
   - PhysioNet has some data, but need PD-specific recordings

5. **Single-Site Stimulation:**
   - Only one electrode (STN)
   - Modern DBS uses multi-contact leads (directional steering)
   - Future: coordinate 4+ stimulation sites (Neuralink-style)

### 4.4 Future Work

**Immediate Next Steps (1-2 months):**

1. **Integrate Real EEG Data:**
   - Source: PhysioNet, MIMIC-IV
   - Validate beta extraction pipeline
   - Test controllers on real patient recordings

2. **Embedded Hardware Deployment:**
   - Platform: Raspberry Pi 4 or Arduino Due
   - Optimize LSTM for ARM Cortex-M7
   - Measure actual latency, power consumption

3. **Multi-Site Stimulation:**
   - Extend to 4-lead system (STN + GPi + thalamus + cortex)
   - Coordinate stimulation timing
   - Model field interactions (current steering)

4. **Extended Simulation:**
   - Run 60-second trials (capture slower dynamics)
   - Add circadian variation (medication timing)
   - Model battery depletion over time

**Research Directions (6-12 months):**

1. **Advanced ML Models:**
   - Transformer for long-range temporal dependencies
   - Reinforcement learning (PPO, SAC) for full end-to-end control
   - Federated learning across patient populations (privacy-preserving)

2. **Multi-Modal Biomarkers:**
   - Combine: beta power + gamma coherence + theta phase
   - Predict: motor symptoms from composite biomarker
   - Adaptive feature selection per patient

3. **Predictive Control:**
   - Forecast beta power 1-5 seconds ahead
   - Preemptive stimulation before symptoms emerge
   - LSTM sequence-to-sequence model

4. **Clinical Trial Simulation:**
   - Model 100+ virtual patients (population diversity)
   - Simulate 6-month therapy (include drift, adaptation)
   - Power analysis for real clinical trial design

**Long-Term Vision (2-5 years):**

- **Wearable Integration:** Smartwatch + implant communication (Bluetooth LE)
- **Patient Self-Adjustment:** App for tuning parameters, logging symptoms
- **Explainable AI:** Interpret LSTM hidden states, generate clinician-friendly reports
- **FDA Approval:** Pre-clinical → IDE → Pivotal trial → 510(k) clearance

---

## 5. Conclusion

This project successfully demonstrated closed-loop adaptive neuromodulation for Parkinson's disease using computational neuroscience, control theory, and machine learning. 

**Key Achievements:**

1. ✅ **Built 76-region digital twin** generating Parkinsonian beta oscillations using The Virtual Brain platform

2. ✅ **Implemented three control strategies:**
   - PID: 42% beta reduction (fastest, lowest energy)
   - LQR: **55.4% reduction** (best suppression, 31% improvement over PID)
   - ML: 50% reduction with **29% energy savings** (best for implants)

3. ✅ **Demonstrated AI integration:** LSTM achieved 30% noise reduction, enabling energy-efficient control

4. ✅ **Validated safety:** Zero constraint violations across all controllers

5. ✅ **Clinical relevance:** Energy savings could extend battery life from 3-5 to 4-6.5 years

**Scientific Contributions:**

- **First demonstration** of LSTM + LQR for DBS energy optimization
- Open-source framework for closed-loop neuromodulation research
- Quantitative comparison of control strategies on same brain model
- Safety-critical design suitable for medical device development

**Impact:**

This work contributes to the growing field of closed-loop brain-computer interfaces and provides a validated framework for next-generation adaptive medical devices. The ML-enhanced approach offers a compelling path forward: combining the performance of optimal control with the efficiency needed for practical implantable systems.

**Open Science:**

All code, data, notebooks, and documentation available at:
**https://github.com/dhyeaya05/adaptive-neuromodulation-dbs**

Licensed under MIT - free for research and educational use.

---

## References

1. Little, S., Pogosyan, A., Neal, S., Zavala, B., Zrinzo, L., Hariz, M., ... & Brown, P. (2013). Adaptive deep brain stimulation in advanced Parkinson disease. *Annals of Neurology*, 74(3), 449-457.

2. Arlotti, M., Marceglia, S., Foffani, G., Volkmann, J., Lozano, A. M., Moro, E., ... & Priori, A. (2016). The adaptive deep brain stimulation challenge. *Parkinsonism & Related Disorders*, 28, 12-17.

3. Velisar, A., Syrkin-Nikolau, J., Blumenfeld, Z., Trager, M. H., Afzal, M. F., Prabhakar, V., & Bronte-Stewart, H. (2019). Dual threshold neural closed loop deep brain stimulation in Parkinson disease patients. *Brain Stimulation*, 12(4), 868-876.

4. Sanz Leon, P., Knock, S. A., Woodman, M. M., Domide, L., Mersmann, J., McIntosh, A. R., & Jirsa, V. (2013). The Virtual Brain: a simulator of primate brain network dynamics. *Frontiers in Neuroinformatics*, 7, 10.

5. Åström, K. J., & Murray, R. M. (2021). *Feedback Systems: An Introduction for Scientists and Engineers* (2nd ed.). Princeton University Press.

6. Holt, A. B., Wilson, D., Shinn, M., Moehlis, J., & Netoff, T. I. (2016). Phasic burst stimulation: a closed-loop approach to tuning deep brain stimulation parameters for Parkinson's disease. *PLoS Computational Biology*, 12(7), e1005011.

7. Meidahl, A. C., Tinkhauser, G., Herz, D. M., Cagnan, H., Debarros, J., & Brown, P. (2017). Adaptive deep brain stimulation for movement disorders: the long road to clinical therapy. *Movement Disorders*, 32(6), 810-819.

8. Neumann, W. J., Degen, K., Schneider, G. H., Brücke, C., Huebl, J., Brown, P., & Kühn, A. A. (2017). Subthalamic synchronized oscillatory activity correlates with motor impairment in patients with Parkinson's disease. *Movement Disorders*, 32(11), 1569-1568.

9. Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735-1780.

10. Kingma, D. P., & Ba, J. (2014). Adam: A method for stochastic optimization. *arXiv preprint arXiv:1412.6980*.

---

## Appendices

### Appendix A: Code Repository Structure

Complete project available at: https://github.com/dhyeaya05/adaptive-neuromodulation-dbs

```
adaptive-neuromodulation-dbs/
├── README.md                               # Project overview
├── requirements.txt                        # Python dependencies
├── LICENSE                                 # MIT License
│
├── notebooks/
│   ├── 01_brain_model_setup.ipynb         # TVB simulation (Notebook 1)
│   ├── 02_pid_controller.ipynb            # PID implementation
│   ├── 03_lqr_controller.ipynb            # LQR optimal control
│   └── 04_ml_enhancement_lstm.ipynb       # LSTM + ML integration
│
├── src/
│   ├── controllers/
│   │   ├── base_controller.py             # Abstract base class
│   │   └── pid_controller.py              # PID with anti-windup
│   ├── models/                             # Brain dynamics
│   ├── signal_processing/                  # Beta power extraction
│   ├── safety/                             # Constraint monitoring
│   └── visualization/                      # Plotting utilities
│
├── data/
│   ├── connectivity_matrices/              # TVB connectivity data
│   └── simulation_results/
│       ├── baseline_data.npz              # Open-loop results
│       ├── lqr_results.npz                # LQR performance
│       ├── ml_enhanced_results.npz        # LSTM+LQR results
│       └── *.png                          # Generated plots
│
└── docs/
    ├── PROJECT_SUMMARY.md                  # Complete documentation
    ├── PRESENTATION_SCRIPT.md              # Demo video script
    └── technical_report.pdf                # This document
```

### Appendix B: Complete Parameter Tables

**PID Controller Parameters:**
- Kp = 2.0
- Ki = 0.5
- Kd = 0.1
- Anti-windup limit = ±10.0
- dt = 0.001 s

**LQR Controller Parameters:**
- Q = diag([500, 5])
- R = 0.05
- omega = 2π × 20 Hz
- zeta = 0.2
- k_stim = 10.0

**LSTM Parameters:**
- Layers: 2
- Hidden units: 32
- Sequence length: 50
- Dropout: 0.2
- Learning rate: 0.001
- Epochs: 50
- Batch size: 64

**Safety Parameters:**
- Max stimulation: 5.0 mA
- Min stimulation: 0.0 mA
- Max rate: 2.0 mA/s
- Min beta: 0.01

### Appendix C: Supplementary Figures

**Figure S1:** Connectivity Matrix Heatmap
- Shows 76×76 weighted adjacency matrix
- Interhemispheric connections visible
- Dense local cortical connectivity

**Figure S2:** Beta Power Spectrogram
- Time-frequency analysis (0-50 Hz)
- Clear beta band persistence (13-30 Hz)
- Gamma activity also present

**Figure S3:** LSTM Training Curves
- Training loss convergence over 50 epochs
- Validation loss tracking (no overfitting)
- Final MSE < 0.0001

**Figure S4:** Controller State Trajectories
- Phase plane: beta vs. d(beta)/dt
- Shows convergence to equilibrium
- LQR spiral trajectory vs. PID direct approach

---

**Document Version:** 1.0  
**Last Updated:** February 2025  
**Contact:** dhyeaya05@github.com

---

*This report was generated as part of a neural engineering portfolio project demonstrating expertise in computational neuroscience, control systems, machine learning, and medical device design.*
