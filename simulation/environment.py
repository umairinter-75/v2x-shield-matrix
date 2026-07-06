import time
import numpy as np
import pandas as pd

class V2XIntersectionSimulator:
    def __init__(self, num_vehicles=3):
        """
        Initializes a mock traffic simulation environment for V2X testing.
        Includes support for emergency vehicles and national disaster alerts.
        """
        self.num_vehicles = num_vehicles
        self.vehicles = {}
        
        # Initialize regular commuter vehicles
        for i in range(num_vehicles):
            v_id = f"VEH_NODE_{1000 + i}"
            self.vehicles[v_id] = {
                "type": "commuter",
                "x": float(i * 20.0),       # Staggered starting positions
                "y": 0.0,                   # Traveling on Lane 0
                "v_x": 20.0,                # 20 m/s speed
                "status": "Normal Driving"
            }
            
        # Add an Emergency Vehicle (Ambulance) behind the pack trying to clear a corridor
        self.vehicles["AMBULANCE_RESCUE"] = {
            "type": "emergency",
            "x": -30.0,                     # Starting well behind the commuters
            "y": 0.0,                       # Same lane
            "v_x": 35.0,                    # Moving much faster (approx 80 mph)
            "status": "Responding to Emergency"
        }
        
    def trigger_national_disaster_alert(self, packets):
        """
        Simulates a secure Roadside Unit (RSU) broadcasting a critical 
        National Disaster Evacuation Alert to all vehicles in range.
        """
        disaster_packet = {
            "node_id": "RSU_DISASTER_BROADCAST",
            "timestamp_sender": time.time(),
            "alert_type": "EARTHQUAKE_WARNING",
            "instructions": "EVACUATE AREA - PROCEED TO HIGHER GROUND",
            "severity": "CRITICAL"
        }
        packets.append(disaster_packet)
        return packets

    def generate_packet_streams(self, time_step=0.1, simulation_tick=0):
        """
        Simulates a chronological tick of network traffic, handling vehicle movement
        and emergency lane-clearing maneuvers.
        """
        current_timestamp = time.time()
        packets = []
        
        # Check if the Ambulance is broadcasting a priority request
        ambulance_pos = self.vehicles["AMBULANCE_RESCUE"]["x"]
        
        for v_id, state in self.vehicles.items():
            # EMERGENCY CORRIDOR LOGIC: 
            # If a commuter vehicle detects the fast ambulance closing in from behind,
            # it safely yields by changing its Y-coordinate (moving to Lane 1) and slowing down.
            if state["type"] == "commuter" and (ambulance_pos < state["x"] < ambulance_pos + 60.0):
                state["y"] = 3.5  # Shift to adjacent lane (3.5 meters over)
                state["v_x"] = 12.0  # Slow down to let the emergency vehicle pass
                state["status"] = "YIELDING: Emergency Corridor Cleared"
            
            # Update positions based on current speed
            state["x"] += state["v_x"] * time_step
            
            # Build the network data packet
            packet = {
                "node_id": v_id,
                "type": state["type"],
                "timestamp_sender": current_timestamp,
                "pos_x": round(state["x"], 2),
                "pos_y": round(state["y"], 2),
                "speed_mph": round(state["v_x"] * 2.237, 1), # Convert m/s to mph for easy reading
                "behavior_status": state["status"]
            }
            packets.append(packet)
            
        # At Tick 3, inject the National Disaster Alert to show network capability
        if simulation_tick == 3:
            packets = self.trigger_national_disaster_alert(packets)
            
        return packets

# --- Local Verification Sandbox ---
if __name__ == "__main__":
    print("🚦 Initializing Advanced V2X Traffic Flow & Smart Corridor Simulator...")
    simulator = V2XIntersectionSimulator(num_vehicles=2)
    
    for tick in range(1, 5):
        print(f"\n==================== SIMULATION TICK {tick} ====================")
        live_packets = simulator.generate_packet_streams(time_step=1.0, simulation_tick=tick)
        
        # Display as a clean matrix
        df = pd.DataFrame(live_packets)
        print(df.to_string(index=False))
        time.sleep(1.0)
