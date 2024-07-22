from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from main import get_db, SuccessResponse
from Models.org_models import Organization, Organization_details, Location, GeoTag

router = APIRouter()

@router.post("api/organization/", response_model=SuccessResponse)
def add_organization(org_details: Organization_details, db: Session = Depends(get_db)):
    org_entry = Organization(
        org_name=org_details.org_name,
        venue=org_details.location.venue,
        latitude=org_details.location.geo_tag.latitude,
        longitude=org_details.location.geo_tag.longitude,
        contact_info=org_details.contact_info,
        bio=org_details.bio
    )
    db.add(org_entry)
    db.commit()
    db.refresh(org_entry)
    return SuccessResponse(message="Organization Added Successfully", success=True)

@router.get("api/organization/{org_id}", response_model=Organization_details)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    org_entry = db.query(Organization).filter(Organization.id == org_id).first()
    if not org_entry:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization_details(
        org_name=org_entry.org_name,
        location=Location(
            venue=org_entry.venue,
            geo_tag=GeoTag(latitude=org_entry.latitude, longitude=org_entry.longitude)
        ),
        contact_info=org_entry.contact_info,
        bio=org_entry.bio
    )