import time
import math

class V2XShieldMatrix:
    def __init__(self):
        # Memory/State Engine: {vehicle_id: [past_messages]}
        self.vehicle_registry = {}
        # Trust Scores: Initialized at 100
        self.trust_scores = {}
        # Simulated Local Sensor Registry (What our vehicle's radar/cameras actually see)
        # Represents verified physical objects within a 100-meter radius
        self.local_radar_tracks = []

    def update_local_sensors(self, verified_positions):
        """Updates the vehicle's onboard radar/camera tracking data"""
        self.local_radar_tracks = verified_positions

    def process_bsm(self, bsm):
        """
        Processes an incoming BSM through all three layers,
        now featuring Layer 3 Neighborhood Consensus.
        """
        v_id = bsm.get("vehicle_id")
        current_pos = (bsm["lat"], bsm["long"])

        if v_id not in self.vehicle_registry:
            self.vehicle_registry[v_id] = []
            self.trust_scores[v_id] = 100.0

        # ---------------------------------------------------------
        # LAYER 1: Network & Protocol Sanity Check
        # ---------------------------------------------------------
        current_time = time.time()
        if abs(current_time - bsm["timestamp"]) > 2.0:
            return self._mitigate(v_id, "DROP", "Layer 1 Flag: Stale message / Replay Attack")

        # ---------------------------------------------------------
        # LAYER 2: Kinematic & Physics Validation
        # ---------------------------------------------------------
        if self.vehicle_registry[v_id]:
            last_bsm = self.vehicle_registry[v_id][-1]
            distance = self._calculate_distance(last_bsm["lat"], last_bsm["long"], bsm["lat"], bsm["long"])
            time_delta = bsm["timestamp"] - last_bsm["timestamp"]

            if time_delta > 0:
                calculated_speed = distance / time_delta
                if calculated_speed > 90.0:
                    self.trust_scores[v_id] -= 40
                    return self._mitigate(v_id, "DROP", f"Layer 2 Flag: Impossible Kinematics ({round(calculated_speed, 1)} m/s)")

        # ---------------------------------------------------------
        # LAYER 3: Spatiotemporal Consensus (Sybil/Ghost Detection)
        # ---------------------------------------------------------
        # Rule A: Identity Overlap (Two cars cannot occupy the exact same space)
        for other_id, messages in self.vehicle_registry.items():
            if other_id != v_id and messages:
                last_other = messages[-1]
                spatial_overlap = self._calculate_distance(bsm["lat"], bsm["long"], last_other["lat"], last_other["long"])
                # If two different IDs claim to be within 0.5 meters of each other while moving
                if spatial_overlap < 0.5 and bsm["speed"] > 1.0:
                    self.trust_scores[v_id] -= 60
                    return self._mitigate(v_id, "BLOCK", f"Layer 3 Flag: Critical Spatial Overlap with {other_id} (Sybil Attack)")

        # Rule B: Sensor Cross-Verification (Does radar see you?)
        if self.local_radar_tracks:
            verified = False
            for sensor_pos in self.local_radar_tracks:
                dist_to_sensor_track = self._calculate_distance(bsm["lat"], bsm["long"], sensor_pos[0], sensor_pos[1])
                if dist_to_sensor_track < 5.0: # Within a 5-meter tolerance window
                    verified = True
                    break
            if not verified:
                self.trust_scores[v_id] -= 30
                return self._mitigate(v_id, "THROTTLE", "Layer 3 Flag: Unverified by Onboard Sensors (Ghost Vehicle)")

        # Critical Threshold Check
        if self.trust_scores[v_id] < 50.0:
            return self._mitigate(v_id, "BLOCK", f"Layer 3 Flag: Trust Score Depleted ({self.trust_scores[v_id]})")

        # Code execution updates history if clear
        self.vehicle_registry[v_id].append(bsm)
        return self._mitigate(v_id, "ALLOW", "All layers clear.")

    def _mitigate(self, vehicle_id, action, reason):
        return {
            "vehicle_id": vehicle_id,
            "action": action,
            "reason": reason,
            "current_trust": self.trust_scores.get(vehicle_id, 100.0)
        }

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        lat_dist = (lat2 - lat1) * 111000
        lon_dist = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_dist**2 + lon_dist**2)


# =====================================================================
# SIMULATION ZONE: SYBIL & GHOST VEHICLE INJECTION
# =====================================================================
if __name__ == "__main__":
    shield = V2XShieldMatrix()
    now = time.time()

    # Tell the shield what our vehicle's radar physical sensors ACTUALLY see near us
    # Onboard radar confirms there is only ONE real car physically next to us at coordinates (37.7749, -122.4194)
    shield.update_local_sensors([ (37.7749, -122.4194) ])

    print("--- Starting Layer 3 Sybil & Ghost Simulation ---\n")

    # 1. Real Car reports (Matches Radar)
    real_car = {"vehicle_id": "REAL_TRUCK_A", "lat": 37.7749, "long": -122.4194, "speed": 10.0, "timestamp": now}
    print("Processing REAL_TRUCK_A:", shield.process_bsm(real_car))

    # 2. Ghost Vehicle Attack (Attacker broadcasts a fake BSM from an ID that radar cannot verify)
    ghost_car = {"vehicle_id": "GHOST_VOLVO_X", "lat": 37.7891, "long": -122.4044, "speed": 12.0, "timestamp": now}
    print("\nProcessing GHOST_VOLVO_X:", shield.process_bsm(ghost_car))

    # 3. Sybil Attack: Identity Cloaking (An attacker spawns a completely new ID at the exact same spot as REAL_TRUCK_A)
    sybil_clone = {"vehicle_id": "FAKE_SEDAN_B", "lat": 37.7749, "long": -122.4194, "speed": 10.0, "timestamp": now}
    print("\nProcessing FAKE_SEDAN_B:", shield.process_bsm(sybil_clone))

