"""Resources API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_api_key
from app.models import Resource
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.services.audit import log_action

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("", response_model=list[ResourceRead])
def list_resources(
    db: Session = Depends(get_db),
    _actor: str = Depends(verify_api_key),
):
    """List all resources."""
    return db.query(Resource).all()


@router.post("", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Create a new resource and log action."""
    resource = Resource(**resource_in.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)

    log_action(db, "resource", resource.id, "created", actor)
    db.commit()

    return resource


@router.patch("/{resource_id}", response_model=ResourceRead)
def update_resource(
    resource_id: UUID,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(verify_api_key),
):
    """Update a specific resource and log the changes."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    update_data = resource_in.model_dump(exclude_unset=True)
    if not update_data:
        return resource

    for field, value in update_data.items():
        setattr(resource, field, value)

    db.add(resource)
    db.commit()
    db.refresh(resource)

    log_action(
        db=db,
        entity_type="resource",
        entity_id=resource.id,
        action="updated",
        actor=actor,
        details={"updated_fields": list(update_data.keys())},
    )
    db.commit()

    return resource
