from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    code: str
    name: str
    color: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Station Schemas
class StationBase(BaseModel):
    code: str
    name: str
    kilometer_post: float

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int

    class Config:
        from_attributes = True

# Batch Schemas
class BatchBase(BaseModel):
    name: str
    product_id: int
    total_volume: float
    started_pumping_at: Optional[datetime] = None

class BatchCreate(BatchBase):
    pass

class Batch(BatchBase):
    id: int
    source_station_id: int
    created_by: int
    created_at: datetime
    finished_pumping_at: Optional[datetime] = None
    status: str
    pumped_volume: float

    class Config:
        from_attributes = True

# Flow Entry Schemas
class FlowEntryBase(BaseModel):
    batch_id: int
    station_id: int
    entry_time: datetime
    hourly_volume: float

class FlowEntryCreate(FlowEntryBase):
    pass

class FlowEntry(FlowEntryBase):
    id: int
    entered_by: int
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    code: str
    name: str
    color: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

# Station Schemas
class StationBase(BaseModel):
    code: str
    name: str
    kilometer_post: float

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int

    class Config:
        from_attributes = True

# Batch Schemas
class BatchBase(BaseModel):
    name: str
    product_id: int
    total_volume: float
    started_pumping_at: Optional[datetime] = None

class BatchCreate(BatchBase):
    pass

class Batch(BatchBase):
    id: int
    source_station_id: int
    created_by: int
    created_at: datetime
    finished_pumping_at: Optional[datetime] = None
    status: str
    pumped_volume: float

    class Config:
        from_attributes = True

# Flow Entry Schemas
class FlowEntryBase(BaseModel):
    batch_id: int
    station_id: int
    entry_time: datetime
    hourly_volume: float

class FlowEntryCreate(FlowEntryBase):
    pass

class FlowEntry(FlowEntryBase):
    id: int
    entered_by: int
    entered_at: datetime

    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Visualization Schemas
class BatchPosition(BaseModel):
    batch_id: int
    batch_name: str
    product_name: str
    color: str
    leading_edge_km: float
    trailing_edge_km: float
    length_km: float
    receiving: bool
    received_volume: float = 0.0

class BatchVisualization(BaseModel):
    timestamp: datetime
    batches: List[BatchPosition]
    total_pipeline_length: float