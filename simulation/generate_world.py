import argparse
import random
import requests
import sys

API_URL = "http://localhost:8000/api"
HEADERS = {"X-API-Key": "change-me"}

# Word banks for random generation
LOCATION_PREFIXES = ["Sector", "Zone", "District", "Area", "Block", "Ward"]
LOCATION_NAMES = ["Alpha", "Beta", "Gamma", "Delta", "Central", "North", "South", "East", "West", "Downtown", "Uptown", "Riverside", "Highlands", "Valley"]
LOCATION_SUFFIXES = ["Shelter", "Hospital", "Evac Center", "Hub", "Plaza", "Station", "Compound"]

RESOURCE_TYPES = ["medical_supplies", "food_water", "rescue_equipment", "transport_vehicles", "communication_gear", "power_generators", "tents_cots"]
RESOURCE_ADJECTIVES = ["Heavy", "Light", "Emergency", "Rapid", "Mobile", "Reserve", "Primary", "Secondary", "Tactical", "Standard"]

TEAM_TYPES = ["medical", "rescue", "logistics", "engineering", "security", "command"]
TEAM_NAMES = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Ghost", "Hunter", "Iron", "Vanguard", "Titan"]

def generate_name(bank_type):
    if bank_type == "location":
        pattern = random.choice([1, 2, 3])
        if pattern == 1:
            return f"{random.choice(LOCATION_PREFIXES)} {random.choice([str(i) for i in range(1, 20)])}"
        elif pattern == 2:
            return f"{random.choice(LOCATION_NAMES)} {random.choice(LOCATION_SUFFIXES)}"
        else:
            return f"{random.choice(LOCATION_NAMES)} {random.choice(LOCATION_PREFIXES)}"
    elif bank_type == "resource":
        return f"{random.choice(RESOURCE_ADJECTIVES)} {random.choice(['Unit', 'Cache', 'Supply', 'Stockpile'])} {random.randint(100, 999)}"
    elif bank_type == "team":
        return f"Team {random.choice(TEAM_NAMES)}"

def create_location():
    data = {
        "name": generate_name("location"),
        "latitude": round(random.uniform(30.0, 45.0), 4),
        "longitude": round(random.uniform(-120.0, -70.0), 4),
        "population": random.randint(100, 50000),
        "priority": random.randint(1, 10),
        "current_status": random.choice(["normal", "affected", "evacuated", "sheltering"])
    }
    resp = requests.post(f"{API_URL}/locations", json=data, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def create_resource(location_id):
    data = {
        "name": generate_name("resource"),
        "resource_type": random.choice(RESOURCE_TYPES),
        "status": random.choice(["available", "assigned", "in_transit", "depleted", "maintenance"]),
        "capacity": random.randint(10, 1000),
        "location_id": location_id
    }
    resp = requests.post(f"{API_URL}/resources", json=data, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def create_team(location_id):
    data = {
        "name": generate_name("team"),
        "team_type": random.choice(TEAM_TYPES),
        "status": random.choice(["available", "deployed", "standby", "off_duty"]),
        "capacity": random.randint(5, 50),
        "location_id": location_id
    }
    resp = requests.post(f"{API_URL}/teams", json=data, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def main():
    parser = argparse.ArgumentParser(description="Generate randomized world state for NEXUS simulation")
    parser.add_argument("--locations", type=int, default=5, help="Number of locations to create")
    parser.add_argument("--resources", type=int, default=15, help="Number of resources to create")
    parser.add_argument("--teams", type=int, default=8, help="Number of teams to create")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible generation")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")

    print(f"Generating {args.locations} locations...")
    location_ids = []
    for _ in range(args.locations):
        loc_id = create_location()
        location_ids.append(loc_id)
    print(f"Created {len(location_ids)} locations.")

    if not location_ids:
        print("Cannot create resources or teams without locations. Exiting.")
        sys.exit(1)

    print(f"Generating {args.resources} resources...")
    for _ in range(args.resources):
        loc_id = random.choice(location_ids)
        create_resource(loc_id)
    print(f"Created {args.resources} resources.")

    print(f"Generating {args.teams} teams...")
    for _ in range(args.teams):
        loc_id = random.choice(location_ids)
        create_team(loc_id)
    print(f"Created {args.teams} teams.")

    print("\nWorld generation complete!")

if __name__ == "__main__":
    main()
