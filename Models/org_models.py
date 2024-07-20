from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
class GeoTag(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    venue: str
    geo_tag: GeoTag

class Organization_details(BaseModel):
    org_name: str
    location:Location
    contact_info: int
    bio: Optional[str]=""
