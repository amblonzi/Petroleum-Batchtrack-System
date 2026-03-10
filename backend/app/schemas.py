from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ── Auth ──────────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ── User ──────────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True


# ── Product ───────────────────────────────────────────────────────────────────
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


# ── Pipeline ──────────────────────────────────────────────────────────────────
class PipelineBase(BaseModel):
    line_number: str       # "L2", "L3", "L4", "L5", "L6"
    name: str
    description: Optional[str] = None
    total_length_km: float
    line_fill_rate: float  # m³/km
    is_active: bool = True

class PipelineCreate(PipelineBase):
    pass

class PipelineUpdate(BaseModel):
    line_fill_rate: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Pipeline(PipelineBase):
    id: int
    class Config:
        from_attributes = True


# ── Station ───────────────────────────────────────────────────────────────────
class StationBase(BaseModel):
    code: str
    name: str
    kilometer_post: float
    station_type: str      # "lifting" | "intermediate" | "receiving"
    pipeline_id: int

class StationCreate(StationBase):
    pass

class Station(StationBase):
    id: int
    class Config:
        from_attributes = True


# ── Batch ─────────────────────────────────────────────────────────────────────
class BatchBase(BaseModel):
    name: str
    product_id: int
    total_volume: float
    started_pumping_at: Optional[datetime] = None

class BatchCreate(BatchBase):
    pass  # pipeline resolved server-side from ?line= query param

class Batch(BatchBase):
    id: int
    pipeline_id: int
    source_station_id: int
    created_by: int
    created_at: datetime
    finished_pumping_at: Optional[datetime] = None
    status: str
    pumped_volume: float
    received_volume: float = 0.0
    product: Optional[Product] = None
    class Config:
        from_attributes = True


# ── FlowEntry ─────────────────────────────────────────────────────────────────
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


# ── Visualization ─────────────────────────────────────────────────────────────
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
    line_fill_rate: float