from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)

class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    kilometer_post = Column(Float, nullable=False)

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    source_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    total_volume = Column(Float, nullable=False)
    started_pumping_at = Column(DateTime(timezone=True), nullable=True)
    finished_pumping_at = Column(DateTime(timezone=True))
    status = Column(String, default="CREATED")
    pumped_volume = Column(Float, default=0.0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product")
    source_station = relationship("Station", foreign_keys=[source_station_id])
    creator = relationship("User")

class FlowEntry(Base):
    __tablename__ = "flow_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    hourly_volume = Column(Float, nullable=False)
    entered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    entered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    batch = relationship("Batch")
    station = relationship("Station")
    user = relationship("User")