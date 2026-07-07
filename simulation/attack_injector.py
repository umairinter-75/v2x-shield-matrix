import time
import copy

class V2XAttackInjector:
    def __init__(self):
        """
        Initializes the threat injection module to simulate malicious 
        network exploits on the V2X data streams.
        """
        pass

    def inject_coordinate_spoofing(self, clean_packets, target_node="VEH_NODE_1000"):
        """
        Simulates a GPS/Coordinate Spoofing Attack.
        Alters the position of a clean node to make it appear suddenly 
        in an physically impossible location (Kinematic Violation).
        """
        corrupted_packets = copy.deepcopy(clean_packets)
        
        for packet in corrupted_packets:
            if packet.get("node_id") == target_node:
                # Suddenly shift the vehicle 150 meters ahead instantaneously
                packet["pos_x"] += 150.0 
                packet["behavior_status"] = "ATTACK_TRIGGERED: Position Spoofed"
                
        return corrupted_packets

    def inject_falsified_priority_exploit(self, clean_packets, target_node="VEH_NODE_1001"):
        """
        Simulates a Sybil/Credential Exploit.
        Forces a standard commuter vehicle node to broadcast malicious metadata, 
        falsely claiming emergency status to manipulate traffic flow.
        """
        corrupted_packets = copy.deepcopy(clean_packets)
        
        for packet in corrupted_packets:
            if packet.get("node_id") == target_node:
                # Maliciously overwrite credentials
                packet["type"] = "emergency"
                packet["node_id"] = "SPOOFED_EMERGENCY_NODE"
                packet["behavior_status"] = "ATTACK_TRIGGERED: Falsified Priority Corridor Request"
                
        return corrupted_packets

# --- Local Sandbox Verification Testing ---
if __name__ == "__main__":
    print("💀 V2X Shield Matrix Threat Injection Framework Active...")
    
    # Mock a single baseline packet for verification testing
    mock_base_packet = [{
        "node_id": "VEH_NODE_1001",
        "type": "commuter",
        "timestamp_sender": time.time(),
        "pos_x": 40.0,
        "pos_y": 0.0,
        "speed_kmh": 72.0,  # Converted to km/h for standard automotive telemetry
        "behavior_status": "Normal Driving"
    }]
    
    injector = V2XAttackInjector()
    
    print("\nExecuting Malicious Exploit Demonstration...")
    hacked_stream = injector.inject_falsified_priority_exploit(mock_base_packet)
    
    print(f"Original Type: {mock_base_packet[0]['type']} | Original ID: {mock_base_packet[0]['node_id']}")
    print(f"Hacked Type:   {hacked_stream[0]['type']}   | Hacked ID:   {hacked_stream[0]['node_id']}")
    print(f"Status Log:    {hacked_stream[0]['behavior_status']}")
