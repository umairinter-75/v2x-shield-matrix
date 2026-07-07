## 🧠 Module 2: Edge AI Behavioral Threat Filtering

### Objective
Module 2 is the behavioral anomaly detection engine of the V2X Shield Matrix. While Module 1 checks static physics per packet, Module 2 evaluates temporal behavior patterns and cross-node signatures. It is specifically designed to expose sophisticated attacks—such as Sybil/masquerade exploits and slow trajectory manipulation—while maintaining a strict processing window of under 10 milliseconds.

### Dual-Track Architecture

* **[Inbound Data]** ──► Temporally Aligned Packets (from Module 1)
   │
   ├──► **Track 1: Inter-Node Parallel Engine**
   │     └── *Global Fingerprinting Analysis* ──► Catches Sybil/Masquerade Loops
   │
   └──► **Track 2: Intra-Node Parallel Engine**
         └── *Lightweight Forest Evaluator* ──► Catches Stealth Trajectory Drift
   │
   ▼
* **[Output Target]** ──► Flagged Threats Forwarded to Module 3 (Trust Engine)

### Core Threat Detection Tracks

#### 1. Global Inter-Node Fingerprinting (`detect_sybil_fingerprints`)
Protects the mesh network against Sybil attacks where a single malicious radio impersonates multiple vehicles to manufacture a phantom gridlock.
* **Mechanism:** Instead of inspecting nodes sequentially, this track clusters the spatial-temporal vectors of all active nodes in the local environment matrix. If multiple distinct `node_id` entries exhibit overlapping velocity components or identical trajectory profiles, the engine flags the nodes for localized cryptographic isolation.

#### 2. Stateful Trajectory Evaluation (`evaluate_lightweight_forest`)
Identifies stealthy coordinate drift attacks where an attacker slowly modifies data streams over time to induce emergency braking maneuvers.
* **Mechanism:** To preserve edge memory and stay within the execution boundary, the system avoids storing deep rolling packet buffers. Instead, it maintains a highly compressed state matrix per active node. This matrix tracks delta deviations in behavior features (e.g., unexpected lateral variance) and passes them through an optimized, tree-based anomaly engine (such as an Isolation Forest).
