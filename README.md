# V2X Shield Matrix

An intelligent, decentralized edge-security framework designed to protect Vehicle-to-Everything (V2X) communication networks from malicious data injection, coordinate spoofing, and sensor manipulation.

## Executive Summary

The V2X Shield Matrix acts as a localized firewall and trust-verification engine running directly on a vehicle's onboard edge computer. As autonomous vehicle networks rely heavily on real-time data from infrastructure (V2I), pedestrians (V2P), and neighboring vehicles (V2V), a single compromised node can cause catastrophic traffic or safety failures. This system ensures that only validated, physically consistent data influences driving decisions.

## Architecture Overview

The system is divided into three core sequentially executed modules:

### Module 1: Sensor Fusion & Temporal Alignment
* **Objective:** Collects asynchronous inbound V2X data streams and cross-references them against the host vehicle’s local physical sensors (low-cost commodity hardware like optical Cameras, standard Radar, Ultrasonic sensors, and GPS) using physics-based dead-reckoning interpolation to verify spatial consistency without relying on expensive infrastructure additions.

## 🛠️ Module 2 Implementation: Edge AI Behavioral Threat Filtering (Active)

Module 2 has transitioned from architectural specification to a functional Python implementation located in `simulation/threat_filter.py`. This module operates as a zero-dependency, ultra-lightweight processing layer optimized for resource-constrained edge computing environments (onboard vehicle computers).

### 📐 Implemented Detection Tracks

1. **Track 1: Inter-Node Spatial-Temporal Fingerprinting (`detect_sybil_fingerprints`)**
   * **Mechanism:** Dynamically keys localized coordinates to identify overlapping physical space signatures.
   * **Target:** Intercepts Sybil/masquerade loops where distinct virtual node IDs report near-identical trajectory matrices and speed indicators to create artificial traffic patterns.

2. **Track 2: Stateful Trajectory Forest Evaluation (`evaluate_lightweight_forest`)**
   * **Mechanism:** Maintains a compressed rolling history matrix (bounded memory tracking windows) per node ID to calculate frame-to-frame delta jumps.
   * **Target:** Identifies kinematic violations, flagging stealthy trajectory drift or sudden instantaneous coordinate teleportation attacks exceeding baseline physics constraints.

---

## 🧪 Verification & Integration Harness

A dedicated test pipeline has been integrated under the `tests/` directory to validate detection accuracy against active spoofing injectors.

### Directory Structure
'''
v2x-shield-matrix/
├── simulation/
│   ├── environment.py
│   ├── attack_injector.py
│   └── threat_filter.py        # Implemented detection engine
└── tests/
    ├── __init__.py
    └── test_threat_filter.py   # Deterministic integration suite

* [UPDATE - July 11] The core kinematic engine and J2735 message parsing architecture have been successfully prototyped and verified in a localized sandbox environment (v2x_shield.py). It actively handles deterministic replay and physics-boundary violations.
* [UPDATE - July 11] Layer 3 Neighborhood Consensus (Sybil/Ghost verification) is now fully operational.

### Module 3: Matrix Trust & Mitigation Engine
* **Objective:** Manages a fluid reputation system (Trust Scores) for surrounding nodes. When an anomaly is verified, this engine drops firewalls at the local OS level to block the attacker's network sockets and signs/broadcasts a cryptographic mesh warning to alert neighboring clean vehicles.

### 🛡️ Module 3 Implementation: Matrix Trust & Mitigation Engine (Active)

Module 3 has transitioned from architectural specifications to a fully operational mitigation, throttling, and mesh-alert pipeline (`v2x_shield.py`). It acts as the adaptive firewall and enforcement layer of the Shield Matrix.

#### 📡 Implemented Mitigation Tracks

1. **Dynamic Hardware Throttling (Resource Protection)**
   * **Mechanism:** When a node's reputation drops into the *Caution Bracket* (50.0 <= Score < 70.0), the firewall enforces a deterministic packet-dropping algorithm.
   * **Action:** It drops 80% of incoming packets (only processing 1 out of every 5 messages), instantly neutralizing high-frequency data floods/DoS storms while conserving vehicle CPU resource blocks.

2. **Temporal Trust Recovery (The Forgiveness Loop)**
   * **Mechanism:** To handle benign anomalies (e.g., temporary GPS multipath degradation under steel bridges), a linear recovery engine tracks telemetry consistency.
   * **Math Formula:** If a vehicle continuously transmits clean, physically compliant data, its score recovers dynamically over time:
     T_new = min(100.0, T_current + (alpha * delta_t))
     *(Where alpha = 0.5 trust points / second)*

3. **Decentralized Over-the-Air Mesh Alerts**
   * **Mechanism:** Incorporates peer-to-peer V2V ad-hoc warning tracking. When a highly reputable vehicle or Roadside Unit (RSU) broadcasts a **Misbehavior Report (MBR)** token, our matrix intercepts it and proactively docks the suspect node by **-30 trust points** before it even attempts to communicate directly with our car.

#### 📊 Verification Validation Matrix (Simulation Benchmarks)
The pipeline successfully validated these exact mitigation stages during live end-to-end sandbox execution logs:
* `GHOST_FORD` (Sensor Anomaly) -> Trust dropped to **65.0** -> Packets 2 through 5 completely **`THROTTLE`**d -> 30-second clean behavior window triggers forgiveness loop -> Trust restored to **80.0** (`ALLOW`).
* `ROGUE_TESLA` (Mesh Intervention) -> Proactively pre-penalized to **70.0** via signed incoming MBR -> Subsequent sensor spoofing anomaly instantly drops score to **30.5** -> Triggers early-exit firewall rejection (`DROP`) moving into permanent containment (`BLOCK`).

## Technical Roadmap & Simulation Sandbox

Immediate development milestones focus on building out the testing framework:
* **Simulation Environment (`/simulation/environment.py`):** A Python-based sandbox mimicking a high-density traffic intersection broadcasting simulated V2X telemetry streams.
* **Data Injection Pipeline (`/simulation/attack_injector.py`):** Automated scripts designed to purposefully inject malicious data packages (such as coordinate jump attacks) to evaluate system resilience.
* **Latency Optimization:** Profiling codebase executions to guarantee an end-to-end processing threshold of under 10 milliseconds per data packet.

## Open-Source Governance & Contributions

This project is being organized as a collaborative, open-source initiative under the Apache 2.0 License.

### Developer Recognition:
* All contributing senior engineers will be prominently credited as Core Project Developers / Maintainers directly within this README.md and primary codebase files.
* Foundational system architecture belongs to the repository owner under the Apache 2.0 framework.

### How to Contribute:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/module-optimization`).
3. Commit your changes (`git commit -m 'Optimize numpy vector calculations'`).
4. Push to the branch (`git push origin feature/module-optimization`).
5. Open a Pull Request.
