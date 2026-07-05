import time
import numpy as np
import pandas as pd

class V2XIntersectionSimulator:
    def __init__(self, num_vehicles=3):
        """
        Initializes a mock traffic simulation environment for V2X testing.
        Each vehicle moves along a simple linear path to simulate telemetry.
        """
        self.num_vehicles = num_vehicles
        self.vehicles = {}
        
        # Initialize baseline mock vehicles with IDs, positions (X, Y in meters), and velocity (m/s)
        for i in range(num_vehicles):
            v_id = f"VEH_NODE_{1000 + i}"
            self.vehicles[v_id] = {
                "x": float(i * 15.0),       # Staggered starting positions
                "y": 0.0,                   # Straight road along the X-axis
                "v_x": 20.0,                # Constant moving speed (approx 45 mph)
                "v_y": 0.0
            }
            
    def generate_packet_streams(self, time_step=0.1):
        """
        Simulates a single chronological tick of network traffic.
        Returns a list of data packets mimicking inbound RF broadcast messages.
        """
        current_timestamp = time.time()
        packets = []
        
        for v_id, state in self.vehicles.items():
            # Update physical coordinates based on constant velocity physics (d = v * t)
            state["x"] += state["v_x"] * time_step
            state["y"] += state["v_y"] * time_step
            
            # Construct standard V2X telemetry broadcast packet
            packet = {
                "node_id": v_id,
                "timestamp_sender": current_timestamp,
                "pos_x": round(state["x"], 3),
                "pos_y": round(state["y"], 3),
                "velocity_x": state["v_x"],
                "velocity_y": state["v_y"]
            }
            packets.append(packet)
            
        return packets

# --- Local Sandbox Verification Testing ---
if __name__ == "__main__":
    print("🚦 Initializing V2X Shield Matrix Simulation Environment...")
    simulator = V2XIntersectionSimulator(num_vehicles=3)
    
    print("\n⚡ Broadcasting live telemetry data packets over 5.9 GHz mesh network topology:")
    # Run a brief 3-step loop to verify packet formats look completely standard
    for step in range(3):
        print(f"\n--- Simulation Tick {step + 1} ---")
        live_packets = simulator.generate_packet_streams()
        
        # Format as a clean Pandas dataframe for terminal logging visualization
        df = pd.DataFrame(live_packets)
        print(df.to_string(index=False))
        
        time.sleep(0.5)  # Brief pause between simulated radio cycles
