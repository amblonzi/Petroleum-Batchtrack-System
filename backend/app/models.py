from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, UniqueConstraint
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
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)


class Pipeline(Base):
    """Represents a KPC pipeline line (L2, L3, L4, L5, L6)."""
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    line_number = Column(String, unique=True, nullable=False)  # "L2", "L3", etc.
    name = Column(String, nullable=False)
    description = Column(String)
    total_length_km = Column(Float, nullable=False)
    line_fill_rate = Column(Float, nullable=False)  # m³/km
    is_active = Column(Boolean, default=True)

    stations = relationship("Station", back_populates="pipeline")
    batches = relationship("Batch", back_populates="pipeline")


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    kilometer_post = Column(Float, nullable=False)
    # "lifting" = injection/pumping origin, "receiving" = terminal, "intermediate" = relay
    station_type = Column(String, nullable=False, default="intermediate")

    pipeline = relationship("Pipeline", back_populates="stations")

    __table_args__ = (
        UniqueConstraint("code", "pipeline_id", name="uq_station_code_pipeline"),
    )


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
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

    pipeline = relationship("Pipeline", back_populates="batches")
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