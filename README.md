### Repository Description

> A simulated flight software pipeline for satellite telemetry FDIR. This purely synthetic environment utilizes a Kalman-Neural Centaur architecture: Linear Kalman Filters handle deterministic physics while GPT-5.1 generates SITREPs during simulated EW jamming events. Built with Poliastro to validate theoretical FDIR logic against synthetic datasets.

---

# Sentinel Node

**Simulated Telemetry FDIR and Synthetic Electronic Warfare Detection Pipeline**

Sentinel Node is a theoretical flight software framework developed to simulate satellite telemetry monitoring and Fault Detection, Isolation, and Recovery (FDIR) protocols within a contested synthetic environment. The project serves as a proof-of-concept for a hybrid Kalman-Neural Centaur architecture, designed to identify non-ballistic anomalies in simulated trajectory data.

## Project Scope and Intent

This project is a purely computational simulation intended for research and educational purposes. It utilizes synthetic datasets to model how autonomous systems might identify coordinate spoofing or sensor jamming in a laboratory setting. All telemetry and threat events are generated programmatically and do not represent actual flight data or real-world satellite operations.

## Architecture and Methodology

* **Synthetic State Estimation**: Employs a Linear Kalman Filter (LKF) to propagate simulated state vectors. This establishes a mathematical baseline for expected orbital positioning within the software's coordinate system.
* **Simulated FDIR Logic**: Implements automated isolation protocols based on synthetic thresholds. If a programmatically generated sensor measurement exceeds a 1.0 km residual, the system isolates the data and relies on dead-reckoning to preserve the integrity of the simulated baseline.
* **Neural Supervision Layer**: Integrates GPT-5.1 to analyze telemetry events that trigger simulation flags. The model generates technical Situation Reports (SITREPs) based on the mathematical discrepancy between the predicted state and the injected threat data.
* **Orbital Simulation Engine**: Generates 3D orbital ground truths using the poliastro and astropy libraries. These tools are used to create a consistent, theoretical environment for testing autonomous logic against curved orbital paths.

## Technical Stack

* **Software Engineering**: Python, NumPy, Linux-compatible ETL pipelines.
* **Simulation Framework**: poliastro, astropy.
* **AI Integration**: OpenAI API (GPT-5.1) using structured JSON output formatting.
* **Visualization Interface**: Simulated telemetry broadcasting via WebSockets to a local OpenSpace instance.

## Performance Validation (Synthetic Stress Test)

The FDIR pipeline was evaluated against a range of simulated threat intensities to determine the effectiveness of the theoretical isolation logic.

| Simulated Threat Intensity | Detection Latency | Accuracy (RMSE) |
| --- | --- | --- |
| 0.5 km (Sub-threshold) | FAILED | 0.5046 km |
| 5.0 km (Overt Spoofing) | 0s | 0.1202 km |
| 50.0 km (Brute Force) | 0s | 0.0341 km |

These results demonstrate the system's ability to maintain a noise-tolerance envelope for minor synthetic variances while achieving instantaneous isolation for major kinematic violations within the simulation.

## Installation and Operational Security

To maintain operational security (OPSEC) and prevent the exposure of credentials, this project utilizes environment variables for all API interactions.

1. **Environment Setup**:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```


2. **Credential Management**:
Configure a local `.env` file in the root directory. This file is included in the `.gitignore` to ensure keys remain local to the user's environment.
```text
OPENAI_API_KEY=your_theoretical_access_key
```


3. **Execution Pipeline**:
The user must initialize the kinematic surrogate generator to produce a synthetic `flight_telemetry.csv` before launching the FDIR monitoring loop.

## About the Developer

Michael Fowler is a Department of War Cost Estimator and systems analyst focusing on autonomous systems and tactical defense technology. He holds an Active Secret Clearance and is a Master of Science candidate in Systems Analysis at the Naval Postgraduate School.
