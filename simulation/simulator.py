import argparse
import random
import time
import requests
import sys
import threading
import json
import sseclient

API_URL = "http://localhost:8000/api"
HEADERS = {"X-API-Key": "change-me"}

EVENT_TYPES = [
    "new_report", 
    "resource_status_change", 
    "resource_failure", 
    "team_status_change", 
    "escalation"
]

def get_world_state():
    resp = requests.get(f"{API_URL}/world-state", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def create_incident():
    incident_types = ["Hurricane", "Earthquake", "Flood", "Wildfire", "Cyber Attack"]
    data = {
        "title": f"{random.choice(incident_types)} Operation {random.randint(100, 999)}",
        "description": "Simulated emergency scenario initiated by simulator.",
        "severity": random.choice(["high", "critical", "medium"])
    }
    resp = requests.post(f"{API_URL}/incidents", json=data, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def generate_event(incident_id, location_id, failure_rate):
    is_failure = random.random() < failure_rate
    event_type = "resource_failure" if is_failure else random.choice(EVENT_TYPES)
    
    data = {
        "incident_id": incident_id,
        "event_type": event_type,
        "source": "simulator",
        "description": f"Simulated event: {event_type} at location {location_id}",
        "location_id": location_id,
        "severity": "high" if is_failure else random.choice(["low", "medium", "high"])
    }
    resp = requests.post(f"{API_URL}/agent/events", json=data, headers=HEADERS)
    if resp.status_code == 201:
        print(f"[SIMULATOR] Created event: {event_type} at location {location_id}")
    else:
        print(f"[SIMULATOR ERROR] Failed to create event: {resp.text}")

def resolve_pending_decisions():
    resp = requests.get(f"{API_URL}/decisions/pending", headers=HEADERS)
    if resp.status_code != 200:
        return False
        
    decisions = resp.json()
    resolved_any = False
    for dec in decisions:
        if dec.get("options") and len(dec["options"]) > 0:
            option = random.choice(dec["options"])
            resolve_data = {
                "selected_option": option,
                "decided_by": "simulator",
                "reason": "auto-resolved by simulator"
            }
            res = requests.post(f"{API_URL}/decisions/{dec['id']}/resolve", json=resolve_data, headers=HEADERS)
            if res.status_code == 200:
                print(f"\n[SIMULATOR] \033[92mAuto-resolved decision '{dec['question']}' with '{option}'\033[0m")
                resolved_any = True
    return resolved_any

def has_pending_decisions():
    resp = requests.get(f"{API_URL}/decisions/pending", headers=HEADERS)
    if resp.status_code == 200 and len(resp.json()) > 0:
        return True
    return False

def stream_activity():
    try:
        response = requests.get(f"{API_URL}/agent/activity", headers=HEADERS, stream=True)
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.event == "agent_activity":
                data = json.loads(event.data)
                actor = data.get("actor", "Agent")
                action = data.get("action", "")
                entity_type = data.get("entity_type", "")
                details = data.get("details", {})
                print(f"\n[AGENT] \033[94m{actor} {action} {entity_type}\033[0m")
                if details:
                    print(f"        {json.dumps(details)}")
    except Exception as e:
        print(f"[AGENT STREAM ERROR] {e}")

def main():
    parser = argparse.ArgumentParser(description="Run simulation against NEXUS world state")
    parser.add_argument("--duration", type=int, default=120, help="Duration to run simulator (seconds)")
    parser.add_argument("--failure-rate", type=float, default=0.1, help="Probability of resource failure events")
    parser.add_argument("--auto-resolve", action="store_true", help="Automatically resolve pending decisions")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    world = get_world_state()
    locations = world.get("locations", [])
    if not locations:
        print("No locations found in world state. Please run generate_world.py first.")
        sys.exit(1)

    print("Creating incident...")
    incident_id = create_incident()
    print(f"Incident created: {incident_id}")

    print("Starting agent activity stream...")
    stream_thread = threading.Thread(target=stream_activity, daemon=True)
    stream_thread.start()

    start_time = time.time()
    print(f"\nStarting simulation loop for {args.duration} seconds...")
    
    while time.time() - start_time < args.duration:
        # Check for decisions
        if has_pending_decisions():
            print("[SIMULATOR] Pending decision detected. Pausing event generation...")
            if args.auto_resolve:
                resolve_pending_decisions()
            # Wait a bit before checking again
            time.sleep(5)
            continue
            
        # Generate event based on exponential distribution (average wait 10s)
        wait_time = random.expovariate(1.0 / 10.0)
        time.sleep(wait_time)
        
        # In case time expired while waiting
        if time.time() - start_time >= args.duration:
            break
            
        loc = random.choice(locations)
        generate_event(incident_id, loc["id"], args.failure_rate)

    print("\nSimulation complete!")

if __name__ == "__main__":
    main()
