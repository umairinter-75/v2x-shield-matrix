import time
import math
import json

class V2XShieldMatrix:
    def __init__(self, vehicle_id="EGO_VEHICLE"):
        self.ego_id = vehicle_id
        self.vehicle_registry = {}
        self.last_seen_registry = {}
        self.trust_scores = {}
        self.packet_counters = {}
        self.local_radar_tracks = []
        self.alpha_recovery = 0.5

        # ACTIVE REGIONAL HAZARDS CONTAINER
        # Stores active disaster hazards: {"HAZARD_TYPE": (lat_min, lon_min, lat_max, lon_max)}
        self.active_geofenced_hazards = {}

    def update_local_sensors(self, verified_positions):
        self.local_radar_tracks = verified_positions

    def inject_disaster_alert(self, hazard_type, bounding_box):
        """MODULE 4: Injects a macro geographic environmental disaster alert into the grid"""
        self.active_geofenced_hazards[hazard_type] = bounding_box
        print(f"⚠️ [DISASTER BROADCAST] MACRO GRID ALERT INJECTED: {hazard_type} zone declared across boundary bounds!")

    def commit_blackbox_snapshot(self, trigger_reason):
        """
        BLACK BOX RECORDER:
        Dumps an immutable forensic state log of all active surrounding vehicles
        and environmental context to a JSON file for post-incident analysis.
        """
        snapshot = {
            "timestamp": time.time(),
            "trigger_event": trigger_reason,
            "ego_vehicle_id": self.ego_id,
            "active_surrounding_vehicles": []
        }

        for v_id in self.trust_scores.keys():
            last_loc = self.vehicle_registry[v_id][-1] if self.vehicle_registry.get(v_id) else None
            snapshot["active_surrounding_vehicles"].append({
                "vehicle_id": v_id,
                "current_trust_score": round(self.trust_scores[v_id], 1),
                "last_reported_position": (last_loc["lat"], last_loc["long"]) if last_loc else "Unknown",
                "packet_history_count": self.packet_counters.get(v_id, 0)
            })

        filename = f"blackbox_snapshot_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(snapshot, f, indent=4)
        print(f"💾 [BLACK BOX COMMIT] Forensic flight log successfully written to disk: '{filename}' due to '{trigger_reason}'!")

    def receive_network_mbr(self, mbr):
        target_id = mbr["target_id"]
        reporter_id = mbr["reporter_id"]
        if self.trust_scores.get(reporter_id, 100.0) >= 80.0:
            if target_id not in self.trust_scores:
                self.trust_scores[target_id] = 100.0
            if self.trust_scores[target_id] >= 50.0:
                self.trust_scores[target_id] = max(0.0, self.trust_scores[target_id] - 30.0)
                print(f"📡 [MESH ALERT] Received valid MBR from {reporter_id}. Proactively docked {target_id} to trust score {self.trust_scores[target_id]}.")

    def process_bsm(self, bsm, virtual_now=None):
        v_id = bsm.get("vehicle_id")
        current_time = bsm["timestamp"]
        sim_now = virtual_now if virtual_now is not None else time.time()

        if v_id not in self.vehicle_registry:
            self.vehicle_registry[v_id] = []
            self.last_seen_registry[v_id] = current_time
            self.packet_counters[v_id] = 0
            if v_id not in self.trust_scores:
                self.trust_scores[v_id] = 100.0

        self.packet_counters[v_id] += 1
        current_trust = self.trust_scores[v_id]

        # 1. Enforcement/Throttling Firewall
        if current_trust < 50.0:
            return self._mitigate(v_id, "BLOCK", f"Firewall Drop: Node is blacklisted ({current_trust})")

        if 50.0 <= current_trust < 70.0:
            if self.packet_counters[v_id] % 5 != 1:
                return self._mitigate(v_id, "THROTTLE", "Hardware Drop: Packet throttled under resource-protection block")

        # 2. Temporal Trust Recovery (The Forgiveness Loop)
        if current_trust < 100.0 and current_trust >= 50.0:
            time_since_last_seen = current_time - self.last_seen_registry[v_id]
            if time_since_last_seen > 0:
                recovery_amount = time_since_last_seen * self.alpha_recovery
                self.trust_scores[v_id] = min(100.0, current_trust + recovery_amount)

        self.last_seen_registry[v_id] = current_time

        # 3. Layer 1: Freshness Check
        if abs(sim_now - bsm["timestamp"]) > 2.0:
            return self._mitigate(v_id, "DROP", "Layer 1 Flag: Stale message / Replay Attack")

        # 4. Layer 2: Kinematics (Dynamic Adaptation via Geographic Disaster Modifiers)
        speed_ceiling = 90.0 # Standard condition speed cap (~200mph)

        # Evaluate if vehicle reporting is inside an active macro hazard geofence
        for hazard, bounds in list(self.active_geofenced_hazards.items()):
            lat_min, lon_min, lat_max, lon_max = bounds
            if lat_min <= bsm["lat"] <= lat_max and lon_min <= bsm["long"] <= lon_max:
                if hazard == "EARTHQUAKE_SEISMIC_RUPTURE":
                    speed_ceiling = min(speed_ceiling, 5.0)
                    print(f"⚠️ [SEISMIC EMERGENCY OVERRIDE] Target vehicle {v_id} caught in active {hazard} zone! Enforcing structural velocity safety ceiling of {speed_ceiling} m/s.")
                elif hazard == "FLASH_FLOOD" or hazard == "BLACK_ICE":
                    speed_ceiling = min(speed_ceiling, 20.0)
                    print(f"🚨 [DYNAMIC OVERRIDE] Target vehicle {v_id} caught in active {hazard} zone. Restricting kinematic velocity threshold to {speed_ceiling} m/s!")

        # INSTANT CRITICAL EMERGENCY CHECK: Evaluate payload speed against environmental caps immediately
        reported_speed = bsm.get("speed", 0.0)
        if reported_speed > speed_ceiling:
            self.trust_scores[v_id] = max(0.0, self.trust_scores[v_id] - 60.0) # Slashes trust straight below 50.0
            self.commit_blackbox_snapshot(f"DISASTER BREAKDOWN: speed violation by {v_id} in disaster zone")
            return self._mitigate(v_id, "BLOCK", f"Disaster Violation: Reported speed ({reported_speed} m/s) violates emergency cap ({speed_ceiling} m/s)")

        if self.vehicle_registry[v_id]:
            last_bsm = self.vehicle_registry[v_id][-1]
            distance = self._calculate_distance(last_bsm["lat"], last_bsm["long"], bsm["lat"], bsm["long"])
            time_delta = bsm["timestamp"] - last_bsm["timestamp"]
            if time_delta > 0:
                calculated_speed = distance / time_delta
                if calculated_speed > speed_ceiling:
                    self.trust_scores[v_id] = max(0.0, self.trust_scores[v_id] - 60.0)
                    self.commit_blackbox_snapshot(f"KINEMATIC BREAKDOWN: Calculated speed violation by {v_id}")
                    return self._mitigate(v_id, "BLOCK", f"Kinematic Violation: Calculated tracking speed ({round(calculated_speed, 1)} m/s) exceeds threshold.")

        # 5. Layer 3: Spatiotemporal Consensus
        if self.local_radar_tracks:
            verified = False
            for sensor_pos in self.local_radar_tracks:
                dist_to_sensor_track = self._calculate_distance(bsm["lat"], bsm["long"], sensor_pos[0], sensor_pos[1])
                if dist_to_sensor_track < 5.0:
                    verified = True
                    break
            if not verified:
                self.trust_scores[v_id] = max(0.0, self.trust_scores[v_id] - 35.0)
                return self._mitigate(v_id, "THROTTLE", "Layer 3 Flag: Unverified by Onboard Sensors (Ghost Vehicle)")

        self.vehicle_registry[v_id].append(bsm)
        return self._mitigate(v_id, "ALLOW", "All layers clear.")

    def _mitigate(self, vehicle_id, action, reason):
        return {
            "vehicle_id": vehicle_id,
            "action": action,
            "reason": reason,
            "current_trust": round(self.trust_scores.get(vehicle_id, 100.0), 1)
        }

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        lat_dist = (lat2 - lat1) * 111000
        lon_dist = (lon2 - lon1) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_dist**2 + lon_dist**2)


if __name__ == "__main__":
    shield = V2XShieldMatrix(vehicle_id="EGO_VEHICLE_MAIN")
    t0 = 1710000000.0

    # Ego tracking cluster setup
    shield.update_local_sensors([(37.7749, -122.4194)])

    print("--- Starting Advanced Shield Matrix (Disaster Engine & Black Box Edition) ---\n")

    # TEST A: Standard Operation Verification
    print("[STEP 1] Regular tracking sequence initialization...")
    normal_bsm = {"vehicle_id": "COMMUTER_CAR", "lat": 37.7749, "long": -122.4194, "speed": 10.0, "timestamp": t0}
    print("Processing COMMUTER_CAR:", shield.process_bsm(normal_bsm, virtual_now=t0))

    # TEST B: Geographic Disaster Override Triggering
    print("\n[STEP 2] Injecting a Regional Flash Flood Warning Geofence from network communications...")
    # Bounding parameters surrounding the vehicle's track area
    shield.inject_disaster_alert("FLASH_FLOOD", (37.7000, -122.5000, 37.8000, -122.4000))

    # TEST C: Seismic Disaster Override Triggering
    print("\n[STEP 4] Injecting a Regional Earthquake Seismic Rupture Warning...")
    shield.inject_disaster_alert("EARTHQUAKE_SEISMIC_RUPTURE", (37.7000, -122.5000, 37.8000, -122.4000))

    # A vehicle attempts to drive at 15 m/s (~33 mph) during an active earthquake.
    # While safe for a flash flood, this completely violates seismic structural restrictions!
    seismic_bsm = {"vehicle_id": "EVACUEE_TRUCK", "lat": 37.7750, "long": -122.4194, "speed": 15.0, "timestamp": t0 + 2.0}
    print("Processing EVACUEE_TRUCK packet:", shield.process_bsm(seismic_bsm, virtual_now=t0 + 2.0))

    # COMMUTER_CAR transmits a brand new packet 1 second later traveling at normal freeway speeds (25 m/s or ~55mph)
    # Under standard boundaries, this is safe. But under FLASH_FLOOD limits, it's flagged as an anomaly!
    flood_bsm = {"vehicle_id": "COMMUTER_CAR", "lat": 37.7752, "long": -122.4191, "speed": 25.0, "timestamp": t0 + 1.0}

    print("\n[STEP 3] COMMUTER_CAR continues driving at normal speeds inside active flash flood boundary...")
    print("Processing COMMUTER_CAR packet 2:", shield.process_bsm(flood_bsm, virtual_now=t0 + 1.0))


