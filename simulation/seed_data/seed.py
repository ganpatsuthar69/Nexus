"""Seed script to populate a small demo world for NEXUS.

Creates 5 locations, 8 resources, 6 teams, 1 incident, and 3 starter policies.
Idempotent: checks for existing data before inserting to avoid duplicates.
"""

import sys
import os
from pathlib import Path
import logging

# Add backend directory to sys.path so we can import from app
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Location, Resource, Team, Incident, Policy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_locations(db: Session):
    locations_data = [
        {"name": "Downtown Community Center", "latitude": 34.0522, "longitude": -118.2437, "population": 500, "priority": 1, "current_status": "sheltering"},
        {"name": "City General Hospital", "latitude": 34.0622, "longitude": -118.2537, "population": 1200, "priority": 5, "current_status": "affected"},
        {"name": "Westside High School", "latitude": 34.0422, "longitude": -118.2637, "population": 0, "priority": 2, "current_status": "normal"},
        {"name": "Centennial Park", "latitude": 34.0722, "longitude": -118.2337, "population": 50, "priority": 1, "current_status": "affected"},
        {"name": "Industrial Warehouse District", "latitude": 34.0322, "longitude": -118.2237, "population": 100, "priority": 3, "current_status": "normal"},
    ]
    
    locations = []
    for data in locations_data:
        loc = db.query(Location).filter_by(name=data["name"]).first()
        if not loc:
            loc = Location(**data)
            db.add(loc)
            logger.info(f"Added Location: {data['name']}")
        else:
            logger.info(f"Location exists: {data['name']}")
        locations.append(loc)
    db.commit()
    return locations


def seed_resources(db: Session, locations: list[Location]):
    hospital = next(loc for loc in locations if "Hospital" in loc.name)
    warehouse = next(loc for loc in locations if "Warehouse" in loc.name)
    school = next(loc for loc in locations if "School" in loc.name)
    
    resources_data = [
        {"name": "Water Tanker Alpha", "resource_type": "water_tanker", "status": "available", "capacity": 5000, "location_id": warehouse.id},
        {"name": "Water Tanker Beta", "resource_type": "water_tanker", "status": "available", "capacity": 5000, "location_id": warehouse.id},
        {"name": "Mobile Generator 1", "resource_type": "generator", "status": "available", "capacity": 100, "location_id": warehouse.id},
        {"name": "Mobile Generator 2", "resource_type": "generator", "status": "available", "capacity": 250, "location_id": warehouse.id},
        {"name": "Trauma Kit Set A", "resource_type": "medical_kit", "status": "available", "capacity": 50, "location_id": hospital.id},
        {"name": "Trauma Kit Set B", "resource_type": "medical_kit", "status": "available", "capacity": 50, "location_id": hospital.id},
        {"name": "Emergency Rations Palette", "resource_type": "food_supply", "status": "available", "capacity": 1000, "location_id": school.id},
        {"name": "Cot & Blanket Bundle", "resource_type": "shelter", "status": "available", "capacity": 200, "location_id": school.id},
    ]
    
    for data in resources_data:
        res = db.query(Resource).filter_by(name=data["name"]).first()
        if not res:
            res = Resource(**data)
            db.add(res)
            logger.info(f"Added Resource: {data['name']}")
        else:
            logger.info(f"Resource exists: {data['name']}")
    db.commit()


def seed_teams(db: Session, locations: list[Location]):
    hospital = next(loc for loc in locations if "Hospital" in loc.name)
    center = next(loc for loc in locations if "Community Center" in loc.name)
    warehouse = next(loc for loc in locations if "Warehouse" in loc.name)
    
    teams_data = [
        {"name": "Med Response Team 1", "team_type": "medical", "status": "available", "capacity": 5, "location_id": hospital.id},
        {"name": "Med Response Team 2", "team_type": "medical", "status": "available", "capacity": 4, "location_id": hospital.id},
        {"name": "Logistics Squad Alpha", "team_type": "logistics", "status": "available", "capacity": 10, "location_id": warehouse.id},
        {"name": "Search & Rescue Unit 4", "team_type": "search_rescue", "status": "standby", "capacity": 8, "location_id": center.id},
        {"name": "Comms Field Team", "team_type": "communication", "status": "available", "capacity": 3, "location_id": center.id},
        {"name": "Water Distribution Vol", "team_type": "water", "status": "available", "capacity": 15, "location_id": warehouse.id},
    ]
    
    for data in teams_data:
        team = db.query(Team).filter_by(name=data["name"]).first()
        if not team:
            team = Team(**data)
            db.add(team)
            logger.info(f"Added Team: {data['name']}")
        else:
            logger.info(f"Team exists: {data['name']}")
    db.commit()


def seed_incidents(db: Session):
    incidents_data = [
        {
            "title": "Summer Heatwave Emergency",
            "description": "Prolonged extreme heat causing power outages and water shortages across multiple districts.",
            "status": "open",
            "severity": "high",
        }
    ]
    
    for data in incidents_data:
        inc = db.query(Incident).filter_by(title=data["title"]).first()
        if not inc:
            inc = Incident(**data)
            db.add(inc)
            logger.info(f"Added Incident: {data['title']}")
        else:
            logger.info(f"Incident exists: {data['title']}")
    db.commit()


def seed_policies(db: Session):
    policies_data = [
        {
            "action_type": "assign_resource",
            "max_impact_scope": "single_resource",
            "requires_human": False,
            "auto_approve_conditions": {"priority_threshold": 3}
        },
        {
            "action_type": "reassign_resource",
            "max_impact_scope": "single_resource",
            "requires_human": True,
            "auto_approve_conditions": None
        },
        {
            "action_type": "evacuate",
            "max_impact_scope": "single_location",
            "requires_human": True,
            "auto_approve_conditions": None
        }
    ]
    
    for data in policies_data:
        pol = db.query(Policy).filter_by(action_type=data["action_type"]).first()
        if not pol:
            pol = Policy(**data)
            db.add(pol)
            logger.info(f"Added Policy: {data['action_type']}")
        else:
            logger.info(f"Policy exists: {data['action_type']}")
    db.commit()


def main():
    logger.info("Starting database seed...")
    db = SessionLocal()
    try:
        locations = seed_locations(db)
        seed_resources(db, locations)
        seed_teams(db, locations)
        seed_incidents(db)
        seed_policies(db)
        logger.info("Seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
