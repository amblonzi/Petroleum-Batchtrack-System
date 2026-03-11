# backend/app/crud.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime
from . import models, schemas
from .utils import get_password_hash


# ══════════════════════════════════════════════════════════════════════════════
# USER
# ══════════════════════════════════════════════════════════════════════════════
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).order_by(models.User.id).all()

def update_user_role(db: Session, user_id: int, is_admin: bool) -> Optional[models.User]:
    user = get_user(db, user_id)
    if not user:
        return None
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True



# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT
# ══════════════════════════════════════════════════════════════════════════════
def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session) -> List[models.Product]:
    return db.query(models.Product).all()


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def create_pipeline(db: Session, pipeline: schemas.PipelineCreate) -> models.Pipeline:
    db_pipeline = models.Pipeline(**pipeline.model_dump())
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline


def get_pipelines(db: Session) -> List[models.Pipeline]:
    return db.query(models.Pipeline).filter(models.Pipeline.is_active == True).all()


def get_pipeline_by_line(db: Session, line_number: str) -> Optional[models.Pipeline]:
    return db.query(models.Pipeline).filter(models.Pipeline.line_number == line_number).first()


def get_pipeline(db: Session, pipeline_id: int) -> Optional[models.Pipeline]:
    return db.query(models.Pipeline).filter(models.Pipeline.id == pipeline_id).first()

def update_pipeline(db: Session, pipeline_id: int, pipeline_update: schemas.PipelineUpdate) -> Optional[models.Pipeline]:
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return None
    for key, value in pipeline_update.model_dump(exclude_unset=True).items():
        setattr(pipeline, key, value)
    db.commit()
    db.refresh(pipeline)
    return pipeline



# ══════════════════════════════════════════════════════════════════════════════
# STATION
# ══════════════════════════════════════════════════════════════════════════════
def get_stations(db: Session, pipeline_id: Optional[int] = None) -> List[models.Station]:
    q = db.query(models.Station)
    if pipeline_id:
        q = q.filter(models.Station.pipeline_id == pipeline_id)
    return q.order_by(models.Station.kilometer_post).all()


def create_station(db: Session, station: schemas.StationCreate) -> models.Station:
    db_station = models.Station(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


def _get_lifting_station(db: Session, pipeline_id: int) -> Optional[models.Station]:
    return (
        db.query(models.Station)
        .filter(
            models.Station.pipeline_id == pipeline_id,
            models.Station.station_type == "lifting",
        )
        .first()
    )


def _get_receiving_stations(db: Session, pipeline_id: int) -> List[models.Station]:
    return (
        db.query(models.Station)
        .filter(
            models.Station.pipeline_id == pipeline_id,
            models.Station.station_type == "receiving",
        )
        .order_by(models.Station.kilometer_post)
        .all()
    )


# ══════════════════════════════════════════════════════════════════════════════
# BATCH
# ══════════════════════════════════════════════════════════════════════════════
def get_batches(db: Session, pipeline_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Batch]:
    q = db.query(models.Batch)
    if pipeline_id:
        q = q.filter(models.Batch.pipeline_id == pipeline_id)
    return q.offset(skip).limit(limit).all()


def get_batch(db: Session, batch_id: int) -> Optional[models.Batch]:
    return db.query(models.Batch).filter(models.Batch.id == batch_id).first()


def create_batch(db: Session, batch: schemas.BatchCreate, pipeline_id: int, user_id: int) -> models.Batch:
    lifting = _get_lifting_station(db, pipeline_id)
    if not lifting:
        raise ValueError(f"No lifting station found for pipeline {pipeline_id}.")
    db_batch = models.Batch(
        **batch.model_dump(),
        pipeline_id=pipeline_id,
        source_station_id=lifting.id,
        created_by=user_id,
        status="CREATED",
        pumped_volume=0.0,
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_batch(db: Session, batch_id: int, batch_update: schemas.BatchCreate) -> Optional[models.Batch]:
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        return None
    for key, value in batch_update.model_dump(exclude_unset=True).items():
        setattr(db_batch, key, value)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def delete_batch(db: Session, batch_id: int) -> bool:
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        return False
    
    # Delete associated flow entries first
    db.query(models.FlowEntry).filter(models.FlowEntry.batch_id == batch_id).delete()
    
    db.delete(db_batch)
    db.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# FLOW ENTRY
# ══════════════════════════════════════════════════════════════════════════════
def get_flow_entries(
    db: Session,
    batch_id: Optional[int] = None,
    station_id: Optional[int] = None,
    pipeline_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.FlowEntry]:
    q = db.query(models.FlowEntry)
    if batch_id:
        q = q.filter(models.FlowEntry.batch_id == batch_id)
    if station_id:
        q = q.filter(models.FlowEntry.station_id == station_id)
    if pipeline_id:
        # Join through batch to filter by pipeline
        q = q.join(models.Batch, models.FlowEntry.batch_id == models.Batch.id).filter(
            models.Batch.pipeline_id == pipeline_id
        )
    return q.order_by(models.FlowEntry.entry_time.desc()).offset(skip).limit(limit).all()


def create_flow_entry(db: Session, flow_entry: schemas.FlowEntryCreate, user_id: int) -> models.FlowEntry:
    station = db.query(models.Station).filter(models.Station.id == flow_entry.station_id).first()
    if not station:
        raise ValueError(f"Station {flow_entry.station_id} not found.")

    if station.station_type not in ("lifting", "receiving"):
        raise ValueError(f"Flow entries only allowed at lifting or receiving stations. {station.code} is '{station.station_type}'.")

    batch = db.query(models.Batch).filter(models.Batch.id == flow_entry.batch_id).first()
    if not batch:
        raise ValueError(f"Batch {flow_entry.batch_id} not found.")

    if batch.pipeline_id != station.pipeline_id:
        raise ValueError("Batch and station belong to different pipelines.")

    if flow_entry.hourly_volume <= 0:
        raise ValueError("Volume must be positive.")

    # Receiving station: validate batch position
    if station.station_type == "receiving":
        positions = get_batch_positions(db, pipeline_id=station.pipeline_id)
        batch_pos = next((p for p in positions if p.batch_id == batch.id), None)
        if not batch_pos:
            raise ValueError("Batch is not currently in the pipeline.")
        if not (batch_pos.trailing_edge_km <= station.kilometer_post <= batch_pos.leading_edge_km):
            raise ValueError(
                f"Batch {batch.name} is not at {station.code} (KM {station.kilometer_post:.2f}). "
                f"Batch is at KM {batch_pos.trailing_edge_km:.2f}–{batch_pos.leading_edge_km:.2f}."
            )

    db_flow = models.FlowEntry(**flow_entry.model_dump(), entered_by=user_id)
    db.add(db_flow)
    db.commit()
    db.refresh(db_flow)

    # Update batch status & pumped volume for lifting station entries
    if station.station_type == "lifting":
        if batch.status == "CREATED":
            batch.status = "PUMPING"
            batch.started_pumping_at = db_flow.entry_time
        batch.pumped_volume += db_flow.hourly_volume
        if batch.pumped_volume >= batch.total_volume:
            batch.status = "COMPLETED"
            batch.finished_pumping_at = db_flow.entry_time
        db.commit()

    return db_flow


# ══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════
def _get_received_volumes(
    db: Session, pipeline_id: int, timestamp: Optional[datetime] = None
) -> Dict[int, float]:
    """Returns {station_id: total_received_volume} for all receiving stations of a pipeline."""
    receiving = _get_receiving_stations(db, pipeline_id)
    result: Dict[int, float] = {}
    for rs in receiving:
        q = db.query(func.sum(models.FlowEntry.hourly_volume)).filter(
            models.FlowEntry.station_id == rs.id
        )
        if timestamp:
            q = q.filter(models.FlowEntry.entry_time <= timestamp)
        result[rs.id] = q.scalar() or 0.0
    return result


def get_batch_received_volume(
    db: Session, batch_id: int, pipeline_id: int, timestamp: Optional[datetime] = None
) -> float:
    rs_ids = [s.id for s in _get_receiving_stations(db, pipeline_id)]
    if not rs_ids:
        return 0.0
    q = db.query(func.sum(models.FlowEntry.hourly_volume)).filter(
        models.FlowEntry.batch_id == batch_id,
        models.FlowEntry.station_id.in_(rs_ids),
    )
    if timestamp:
        q = q.filter(models.FlowEntry.entry_time <= timestamp)
    return q.scalar() or 0.0


def get_batch_positions(
    db: Session, pipeline_id: int, timestamp: Optional[datetime] = None
) -> List[schemas.BatchPosition]:
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return []

    LINE_CONTENT = pipeline.line_fill_rate
    lifting = _get_lifting_station(db, pipeline_id)
    if not lifting:
        return []

    receiving_stations = _get_receiving_stations(db, pipeline_id)
    received_vols = _get_received_volumes(db, pipeline_id, timestamp)
    # List of (km_post, received_vol) sorted by km
    rs_sorted = [(rs.kilometer_post, received_vols.get(rs.id, 0.0)) for rs in receiving_stations]

    def vol_to_km(injected_vol: float) -> float:
        adjusted = injected_vol
        for rs_km, rs_received in rs_sorted:
            seg_vol = rs_km * LINE_CONTENT
            if adjusted <= seg_vol:
                return adjusted / LINE_CONTENT
            adjusted -= rs_received
            if adjusted <= seg_vol:
                return rs_km
        return adjusted / LINE_CONTENT

    # Get active batches for this pipeline
    q = (
        db.query(models.Batch)
        .options(joinedload(models.Batch.product))
        .filter(models.Batch.pipeline_id == pipeline_id)
    )
    if timestamp:
        q = q.filter(models.Batch.started_pumping_at <= timestamp)
    else:
        q = q.filter(models.Batch.status.in_(["PUMPING", "COMPLETED"]))
        q = q.filter(models.Batch.started_pumping_at.isnot(None))

    batches = q.order_by(models.Batch.started_pumping_at.desc()).all()

    results: List[schemas.BatchPosition] = []
    injected_so_far = 0.0

    for batch in batches:
        if timestamp:
            pumped_vol = (
                db.query(func.sum(models.FlowEntry.hourly_volume))
                .filter(
                    models.FlowEntry.batch_id == batch.id,
                    models.FlowEntry.station_id == lifting.id,
                    models.FlowEntry.entry_time <= timestamp,
                )
                .scalar()
                or 0.0
            )
            if pumped_vol == 0:
                continue
        else:
            pumped_vol = batch.pumped_volume if batch.status == "PUMPING" else batch.total_volume

        batch_received = get_batch_received_volume(db, batch.id, pipeline_id, timestamp)
        trailing_km = vol_to_km(injected_so_far)
        leading_km = vol_to_km(injected_so_far + pumped_vol)

        receiving = any(
            leading_km >= rs_km and rv > 0 for rs_km, rv in rs_sorted
        )

        results.append(
            schemas.BatchPosition(
                batch_id=batch.id,
                batch_name=batch.name,
                product_name=batch.product.name if batch.product else "Unknown",
                color=batch.product.color if batch.product else "#000000",
                leading_edge_km=leading_km,
                trailing_edge_km=trailing_km,
                length_km=pumped_vol / LINE_CONTENT,
                receiving=receiving,
                received_volume=batch_received,
            )
        )
        injected_so_far += pumped_vol
        if trailing_km > pipeline.total_length_km:
            break

    return results


def get_received_volumes_for_api(
    db: Session, pipeline_id: int, timestamp: Optional[datetime] = None
) -> Dict[int, float]:
    return _get_received_volumes(db, pipeline_id, timestamp)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════════════
def clear_operational_data(db: Session) -> dict:
    try:
        num_flows = db.query(models.FlowEntry).delete()
        num_batches = db.query(models.Batch).delete()
        db.commit()
        return {"deleted_flow_entries": num_flows, "deleted_batches": num_batches}
    except Exception as e:
        db.rollback()
        raise e

def clear_pipeline_data(db: Session, pipeline_id: int) -> dict:
    try:
        # Flow entries are linked to batches. We must delete flow entries for this pipeline's batches first.
        pipeline_batches = db.query(models.Batch.id).filter(models.Batch.pipeline_id == pipeline_id).all()
        batch_ids = [b.id for b in pipeline_batches]
        
        num_flows = 0
        if batch_ids:
            num_flows = db.query(models.FlowEntry).filter(models.FlowEntry.batch_id.in_(batch_ids)).delete(synchronize_session=False)
        
        num_batches = db.query(models.Batch).filter(models.Batch.pipeline_id == pipeline_id).delete(synchronize_session=False)
        db.commit()
        return {"deleted_flow_entries": num_flows, "deleted_batches": num_batches}
    except Exception as e:
        db.rollback()
        raise e

