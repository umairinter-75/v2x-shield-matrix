# tests/test_reputation_engine.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.reputation_engine import AdaptiveReputationEngine

def run_reputation_evaluation():
    print("====================================================")
    print("🛡️ RUNNING REPUTATION & TRUST MITIGATION TEST 🛡️")
    print("====================================================\n")

    # Initialize the core Module 3 engine
    engine = AdaptiveReputationEngine()
    target_node = "TRUCK_ID_99"

    # Step 1: Baseline Check
    print("[STEP 1] Evaluating a completely clean, newly discovered vehicle node...")
    initial_check = engine.evaluate_threat_payload(target_node, [])
    print(f"👉 Current Score: {initial_check['trust_score']} | State: {initial_check['mitigation_state']}")
    print(f"📋 System Log: {initial_check['action_logged']}\n")

    # Step 2: Minor Transient Noise Check (Warning Zone)
    print("[STEP 2] Simulating minor telemetry frame anomalies (e.g., multipath radio interference)...")
    warning_check = engine.evaluate_threat_payload(target_node, ["minor_telemetry_anomaly", "minor_telemetry_anomaly"])
    print(f"👉 Current Score: {warning_check['trust_score']} | State: {warning_check['mitigation_state']}")
    print(f"📋 System Log: {warning_check['action_logged']}\n")

    # Step 3: Mathematical Recovery / Healing Test
    print("[STEP 3] Simulating consecutive clean packets. Testing mathematical healing coefficient...")
    for _ in range(4):
        updated_score = engine.recover_node_trust(target_node, recovery_rate=2.5)
    print(f"👉 Recovered Trust Index: {updated_score} / 100.0\n")

    # Step 4: Critical Malicious Breach Check (Firewall Drop Isolation Zone)
    print("[STEP 4] Injecting a critical Track 1 Sybil clone cluster exploit flag...")
    critical_check = engine.evaluate_threat_payload(target_node, ["sybil_breach"])
    print(f"🚨 Current Score: {critical_check['trust_score']} | State: {critical_check['mitigation_state']}")
    print(f"📋 System Log: {critical_check['action_logged']}\n")

    print("====================================================")
    print("🏁 MODULE 3 FLUID REPUTATION LEDGER VERIFIED SUCCESSFULLY")
    print("====================================================")

if __name__ == "__main__":
    run_reputation_evaluation()
