from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

class Payload(BaseModel):
    meter_id: str = Field(..., example="MTR_IKEJA_01")
    zone: str = Field(..., example="Ikeja")
    voltage: float = Field(..., ge=0, le=400, example=230.5) #ge and le  being > and <
    current: float = Field(..., ge=0, example=14.2)

class MeterStatus(BaseModel):
    meter_id: str
    zone: str
    voltage: float
    current: float
    kwh_consumed: float
    status: str
    last_updated: str
