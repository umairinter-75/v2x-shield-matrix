import time
import math

class V2XShieldMatrix:
    def __init__(self):
        # Memory/State Engine: Stores history of vehicles {vehicle_id: [past_messages]}
        self.vehicle_registry = {}
        # Trust Scores: Initialized at 100 for every new vehicle
        self.trust_scores = {}

    def process_bsm(self, bsm):
        """
        The core entry point. Processes an incoming Basic Safety Message
        through the integrated Shield Matrix layers.
        """
        v_id = bsm.get("vehicle_id")

        # Initialize vehicle state if it's new
        if v_id not in self.vehicle_registry:
            self.vehicle_registry[v_id] = []
            self.trust_scores[v_id] = 100.0

        # ---------------------------------------------------------
        # LAYER 1: Network & Protocol Sanity Check
        # ---------------------------------------------------------
        current_time = time.time()
        if abs(current_time - bsm["timestamp"]) > 2.0:  # 2-second threshold
            return self._mitigate(v_id, "DROP", "Layer 1 Flag: Stale message / Replay Attack")

        # ---------------------------------------------------------
        # LAYER 2: Kinematic & Physics Validation
        # ---------------------------------------------------------
        if self.vehicle_registry[v_id]:
            last_bsm = self.vehicle_registry[v_id][-1]

            # Calculate physical distance moved since last message
            distance = self._calculate_distance(last_bsm["lat"], last_bsm["long"], bsm["lat"], bsm["long"])
            time_delta = bsm["timestamp"] - last_bsm["timestamp"]

            if time_delta > 0:
                calculated_speed = distance / time_delta # meters per second
                # Check for impossible physical acceleration/speed (e.g., > 90 m/s or ~200 mph)
                if calculated_speed > 90.0:
                    self.trust_scores[v_id] -= 40 # Penalize trust score
                    return self._mitigate(v_id, "DROP", f"Layer 2 Flag: Impossible Kinematics ({round(calculated_speed, 1)} m/s)")

        # ---------------------------------------------------------
        # LAYER 3: State & Historical Consensus Trust
        # ---------------------------------------------------------
        # If trust score drops below critical threshold due to repeated anomalies
        if self.trust_scores[v_id] < 50.0:
            return self._mitigate(v_id, "BLOCK", f"Layer 3 Flag: Vehicle Trust Score Critical ({self.trust_scores[v_id]})")

        # If it passes all layers, update its history and ALLOW the message
        self.vehicle_registry[v_id].append(bsm)
        return self._mitigate(v_id, "ALLOW", "All layers clear.")

    def _mitigate(self, vehicle_id, action, reason):
        """
        Output Action Engine: Determines how the vehicle reacts to the decision
        """
        return {
            "vehicle_id": vehicle_id,
            "action": action,  # ALLOW, THROTTLE, DROP, BLOCK
            "reason": reason,
            "current_trust": self.trust_scores.get(vehicle_id, 100.0)
        }

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        A simple approximation formula for distance between two coordinates
        """
        # Multipliers for coordinates to meters (rough approximation for performance)
        lat_dist = (lat2 - lat1) * 111000
        lon_dist = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_dist**2 + lon_dist**2)


# =====================================================================
# SIMULATION / TESTING ZONE
# =====================================================================
if __name__ == "__main__":
    shield = V2XShieldMatrix()
    now = time.time()

    print("--- Starting V2X Shield Matrix Simulation ---\n")

    # 1. Normal Message Simulation
    normal_bsm = {"vehicle_id": "CAR_01", "lat": 37.7749, "long": -122.4194, "speed": 15.0, "timestamp": now}
    print("Sending Normal BSM:", shield.process_bsm(normal_bsm))

    # 2. Layer 1 Attack Simulation (Replay/Old Message)
    stale_bsm = {"vehicle_id": "CAR_02", "lat": 37.7749, "long": -122.4194, "speed": 15.0, "timestamp": now - 10.0}
    print("\nSending Stale BSM:", shield.process_bsm(stale_bsm))

    # 3. Layer 2 Attack Simulation (GPS Spoofing / Teleportation)
    # Moving CAR_01 drastically in 0.1 seconds
    spoofed_bsm = {"vehicle_id": "CAR_01", "lat": 38.9999, "long": -121.4194, "speed": 15.0, "timestamp": now + 0.1}
    print("\nSending Spoofed BSM:", shield.process_bsm(spoofed_bsm))
