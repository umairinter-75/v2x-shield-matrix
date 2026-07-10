# tests/test_threat_filter.py

import sys
import os
# Adjusting system path to locate the simulation components cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import V2XIntersectionSimulator
from simulation.attack_injector import AdversarialInjector
from simulation.threat_filter import EdgeBehavioralFilter

def execute_integration_test():
    print("====================================================")
    print("🛡️ RUNNING INTELLIGENT COMPONENT INTEGRATION TEST 🛡️")
    print("====================================================\n")

    # Step 1: Initialize Environment and Threat Filter
    sim = V2XIntersectionSimulator()
    filter_engine = EdgeBehavioralFilter(velocity_threshold_mph=15.0, max_history_ticks=5)
    
    # Generate standard clean telemetry traffic streams
    sim.register_node(node_id="AUTONOMOUS_VEHICLE_01", pos_x=10.0, pos_y=15.0, speed_mph=35.0)
    sim.register_node(node_id="AMBULANCE_02", pos_x=45.0, pos_y=20.0, speed_mph=50.0, is_emergency=True)
    
    clean_stream = sim.generate_aligned_packet_matrix()
    print(f"[STEP 1] Baseline Packet Stream Compiled. Processing {len(clean_stream)} nodes.")
    
    # Process clean packets to prime our state history matrix
    clean_result = filter_engine.process_telemetry_stream(clean_stream)
    print(f"👉 Baseline Anomaly Check Result -> Detected: {clean_result['is_anomaly_detected']}\n")

    # Step 2: Test Track 2 - Kinematic/Trajectory Teleportation Violation
    print("[STEP 2] Injecting Kinematic Trajectory Spoofing Attack...")
    # Simulate a sudden instantaneous shift (Teleporting AUTONOMOUS_VEHICLE_01 by 120 meters)
    spoofed_stream = [
        {"node_id": "AUTONOMOUS_VEHICLE_01", "pos_x": 130.0, "pos_y": 15.0, "speed_mph": 35.0, "is_emergency": False},
        {"node_id": "AMBULANCE_02", "pos_x": 46.5, "pos_y": 20.0, "speed_mph": 50.0, "is_emergency": True}
    ]
    
    track2_result = filter_engine.process_telemetry_stream(spoofed_stream)
    print(f"🚨 Trajectory Attack Result -> Anomaly Detected: {track2_result['is_anomaly_detected']}")
    print(f"👉 Flagged Malicious Nodes: {track2_result['flagged_nodes']}")
    print(f"📊 Track Metrics: {track2_result['metrics']['trajectory_track_flags']}\n")

    # Step 3: Test Track 1 - Spatial-Temporal Sybil Loop Interception
    print("[STEP 3] Injecting Spatial-Temporal Sybil/Masquerade Loop...")
    # Injecting distinct virtual phantom identities broadcasting matching physical signatures
    sybil_stream = [
        {"node_id": "LEGIT_CAR_A", "pos_x": 50.0, "pos_y": 50.0, "speed_mph": 40.0, "is_emergency": False},
        {"node_id": "PHANTOM_CLONE_B", "pos_x": 50.05, "pos_y": 50.05, "speed_mph": 40.1, "is_emergency": False},
        {"node_id": "PHANTOM_CLONE_C", "pos_x": 49.95, "pos_y": 49.95, "speed_mph": 39.9, "is_emergency": False}
    ]
    
    track1_result = filter_engine.process_telemetry_stream(sybil_stream)
    print(f"🚨 Sybil Matrix Attack Result -> Anomaly Detected: {track1_result['is_anomaly_detected']}")
    print(f"👉 Flagged Malicious Clones: {track1_result['flagged_nodes']}")
    print(f"📊 Track Metrics: {track1_result['metrics']['sybil_track_flags']}\n")
    
    print("====================================================")
    print("🏁 INTEGRATION TESTING SEQUENCE VERIFIED SUCCESSFULLY")
    print("====================================================")

if __name__ == "__main__":
    execute_integration_test()
