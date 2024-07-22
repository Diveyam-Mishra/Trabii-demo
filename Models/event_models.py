from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class GeoTag(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    venue: str
    geo_tag: GeoTag

class PriceFees(BaseModel):
    standard: float
    early_bird: float
    group_rate: float

class DateTimeRange(BaseModel):
    start: datetime
    end: datetime

class HostInformation(BaseModel):
    name: str
    contact_details: str
    bio: str

class EventDetails(BaseModel):
    event_name: str
    event_description: str
    event_type: List[str]
    date_and_time: DateTimeRange
    duration: str
    age_group: str
    family_friendly: bool
    price_fees: PriceFees
    capacity: int
    host_information: HostInformation
    media_files: Optional[List[str]] = [] 

class EventSchema(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    event_ID: str
    created_at: datetime
    updated_at: datetime
    title: str
    date: datetime
    location: Location
    popularity: int
    event_details: EventDetails

