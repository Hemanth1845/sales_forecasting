from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Product(BaseModel):
    brand: str
    model: str
    price: float
    ram: int
    storage: int
    battery: int
    camera_mp: int
    os: str
    launch_date: str

class SalesData(BaseModel):
    model: str
    month: str
    units_sold: int
    revenue: float
    promotions: bool
    competitor_launch: bool

class SimulationRequest(BaseModel):
    model_name: str
    price: float
    ram: int
    camera_mp: int
    battery: int

class ChatRequest(BaseModel):
    query: str
    context: Optional[dict] = None