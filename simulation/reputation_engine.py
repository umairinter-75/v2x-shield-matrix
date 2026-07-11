# simulation/reputation_engine.py
import numpy as np

class AdaptiveReputationEngine:
    def __init__(self, initial_trust=100.0, warning_threshold=75.0, isolation_threshold=50.0):
        """
        Initializes the Adaptive Reputation and Trust Engine (Module 3).
        
        :param initial_trust: Starting score for any newly discovered node (Default: 100.0)
        :param warning_threshold: Trust score below which actions are cross-verified (Default: 75.0)
        :param isolation_threshold: Trust score below which firewall isolation triggers (Default: 50.0)
        """
        self.initial_trust = initial_trust
        self.warning_threshold = warning_threshold
        self.isolation_threshold = isolation_threshold
        
        # Memory map to store the running trust score of active network nodes: {node_id: current_trust_score}
        self.reputation_matrix = {}
        
        # Penalty configuration matrices mapped directly to Module 2 anomaly tracking outputs
        self.penalty_map = {
            "minor_telemetry_anomaly": 10.0,
            "trajectory_anomaly": 35.0,
            "sybil_breach": 60.0
        }

    def _initialize_node_if_new(self, node_id):
        """Ensures a node exists inside our fluid reputation ledger."""
        if node_id not in self.reputation_matrix:
            self.reputation_matrix[node_id] = self.initial_trust

    def evaluate_threat_payload(self, node_id, detected_anomalies):
        """
        Processes raw anomaly feedback parameters from Module 2 for a specific node ID,
        applies dynamic trust decay, and returns its updated mitigation status.
        
        :param node_id: Unique string identifier of the transmitting vehicle node
        :param detected_anomalies: List of strings matching keys inside the penalty_map
        :return: Dict containing updated trust score and current security containment state
        """
        self._initialize_node_if_new(node_id)
        
        # Process and sum all applicable penalties incurred during this telemetry frame
        total_penalty = 0.0
        for anomaly in detected_anomalies:
            if anomaly in self.penalty_map:
                total_penalty += self.penalty_map[anomaly]
                
        # Deduct total calculated penalty from current fluid trust tracking index
        self.reputation_matrix[node_id] = max(0.0, self.reputation_matrix[node_id] - total_penalty)
        current_score = self.reputation_matrix[node_id]
        
        # Fluid Mitigative State Evaluation Engine
        if current_score < self.isolation_threshold:
            state = "ISOLATED_FIREWALL_DROP"
            action_log = f"⚠️ CRITICAL: Dropping OS-level network sockets for node {node_id}. Broadcasting signed cryptographic warning mesh."
        elif current_score < self.warning_threshold:
            state = "WARNING_SUSPICIOUS"
            action_log = f"🔸 WARNING: Node {node_id} marked suspicious. Flagging payload for multi-node consensus verification."
        else:
            state = "SAFE_ZONE"
            action_log = f"✅ PASS: Node {node_id} cleared for automatic routing."

        return {
            "node_id": node_id,
            "trust_score": current_score,
            "mitigation_state": state,
            "action_logged": action_log
        }

    def recover_node_trust(self, node_id, recovery_rate=2.5):
        """
        Applies a positive mathematical healing coefficient for benign frame streams.
        Allows nodes to naturally recover from transient noise/fading penalties over time.
        """
        if node_id in self.reputation_matrix:
            self.reputation_matrix[node_id] = min(self.initial_trust, self.reputation_matrix[node_id] + recovery_rate)
        return self.reputation_matrix.get(node_id, self.initial_trust)
