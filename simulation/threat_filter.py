import numpy as np
from collections import defaultdict

class EdgeBehavioralFilter:
    def __init__(self, velocity_threshold_mph=15.0, max_history_ticks=5):
        """
        Initializes the edge-based behavioral anomaly detection engine.
        
        :param velocity_threshold_mph: Max allowable variance before flagging Sybil clones
        :param max_history_ticks: Size of compressed tracking state matrix per node
        """
        self.velocity_threshold_mph = velocity_threshold_mph
        self.max_history_ticks = max_history_ticks
        
        # Compressed state matrix tracking: {node_id: [list of historical positions/speeds]}
        self.state_matrix = defaultdict(list)

    def detect_sybil_fingerprints(self, aligned_packets):
        """
        Track 1: Global Inter-Node Fingerprinting
        Clusters the spatial-temporal vectors of all active nodes in the local matrix.
        If multiple distinct node_ids exhibit identical/overlapping trajectories, 
        it flags a Sybil/masquerade attack loop attempting phantom gridlock.
        """
        flagged_nodes = set()
        if len(aligned_packets) < 2:
            return list(flagged_nodes)

        # Map positions to check for overlapping physical space anomalies
        # Structure: {(round(pos_x, 1), round(pos_y, 1)): [node_id, speed_mph]}
        spatial_clusters = defaultdict(list)

        for packet in aligned_packets:
            node_id = packet.get("node_id")
            pos_x = packet.get("pos_x", 0.0)
            pos_y = packet.get("pos_y", 0.0)
            speed = packet.get("speed_mph", 0.0)
            
            # Key on roughly localized coordinates to catch overlapping signatures
            coord_key = (round(pos_x, 1), round(pos_y, 1))
            spatial_clusters[coord_key].append((node_id, speed))

        # Evaluate clusters for multi-identity physical convergence
        for coord, nodes in spatial_clusters.items():
            if len(nodes) > 1:
                # Extract speeds to verify if they match or fall within tight bounds
                speeds = [n[1] for n in nodes]
                node_ids = [n[0] for n in nodes]
                
                # If distinct IDs move perfectly in lockstep at the same location
                if np.std(speeds) < (self.velocity_threshold_mph / 2.0):
                    # Flag all nodes involved in this anomalous physical overlapping signature
                    for nid in node_ids:
                        flagged_nodes.add(nid)
                        
        return list(flagged_nodes)

    def evaluate_lightweight_forest(self, aligned_packets):
        """
        Track 2: Stateful Trajectory Evaluation
        Evaluates temporal behavior patterns per individual node over time to catch 
        stealthy, creeping coordinate drift attacks that bypass static snapshot thresholds.
        """
        flagged_nodes = set()

        for packet in aligned_packets:
            node_id = packet.get("node_id")
            pos_x = packet.get("pos_x", 0.0)
            pos_y = packet.get("pos_y", 0.0)
            speed_mph = packet.get("speed_mph", 0.0)
            
            # Step A: Update the highly compressed tracking state matrix
            history = self.state_matrix[node_id]
            history.append({"x": pos_x, "y": pos_y, "speed": speed_mph})
            
            # Maintain strict edge memory window boundary
            if len(history) > self.max_history_ticks:
                history.pop(0)
                
            # Step B: Perform trajectory consistency validation if history is primed
            if len(history) >= 3:
                # Calculate the instantaneous physical jumps between consecutive packets
                deltas = []
                for i in range(1, len(history)):
                    dx = history[i]["x"] - history[i-1]["x"]
                    dy = history[i]["y"] - history[i-1]["y"]
                    distance = np.sqrt(dx**2 + dy**2)
                    deltas.append(distance)
                
                # Check for kinematic violations (e.g., sudden instantaneous jump of 150m)
                # Max speed limit safety margin: 120 mph translates to ~1.8 meters per 33ms tick
                if any(d > 50.0 for d in deltas): 
                    flagged_nodes.add(node_id)
                    
        return list(flagged_nodes)

    def process_telemetry_stream(self, aligned_packets):
        """
        Aggregates parallel execution tracks and formats threats for Module 3.
        """
        sybil_threats = self.detect_sybil_fingerprints(aligned_packets)
        trajectory_threats = self.evaluate_lightweight_forest(aligned_packets)
        
        # Combine all unique flagged threats
        all_threats = list(set(sybil_threats + trajectory_threats))
        
        output_payload = {
            "is_anomaly_detected": len(all_threats) > 0,
            "flagged_nodes": all_threats,
            "metrics": {
                "sybil_track_flags": sybil_threats,
                "trajectory_track_flags": trajectory_threats
            }
        }
        return output_payload
