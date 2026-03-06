# backend/app/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from . import models, schemas
from .utils import get_password_hash

# ====================== USER ======================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ====================== PRODUCT ======================

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

# ====================== STATION ======================

def get_stations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Station]:
    return (
        db.query(models.Station)
        .order_by(models.Station.kilometer_post)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_station(db: Session, station_id: int) -> Optional[models.Station]:
    return db.query(models.Station).filter(models.Station.id == station_id).first()


def create_station(db: Session, station: schemas.StationCreate) -> models.Station:
    db_station = models.Station(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

# ====================== BATCH ======================

def get_batches(db: Session, skip: int = 0, limit: int = 100) -> List[models.Batch]:
    return db.query(models.Batch).offset(skip).limit(limit).all()


def get_batch(db: Session, batch_id: int) -> Optional[models.Batch]:
    return db.query(models.Batch).filter(models.Batch.id == batch_id).first()


def create_batch(db: Session, batch: schemas.BatchCreate, user_id: int) -> models.Batch:
    ps1 = db.query(models.Station).filter(models.Station.code == "PS1").first()
    if not ps1:
        raise ValueError("Source station PS1 not found. Run init_db.py first.")
    db_batch = models.Batch(
        **batch.model_dump(),
        source_station_id=ps1.id,
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

# ====================== FLOW ENTRY ======================

def get_flow_entries(
    db: Session, 
    batch_id: Optional[int] = None, 
    station_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[models.FlowEntry]:
    query = db.query(models.FlowEntry)
    if batch_id:
        query = query.filter(models.FlowEntry.batch_id == batch_id)
    if station_id:
        query = query.filter(models.FlowEntry.station_id == station_id)
    
    return query.order_by(models.FlowEntry.entry_time.desc()).offset(skip).limit(limit).all()


def create_flow_entry(
    db: Session, flow_entry: schemas.FlowEntryCreate, user_id: int
) -> models.FlowEntry:
    # Validate station
    station = db.query(models.Station).filter(models.Station.id == flow_entry.station_id).first()
    if not station:
        raise ValueError(f"Station with ID {flow_entry.station_id} not found.")
    # Only allow specific stations
    if station.code not in ["PS1", "PS8", "PS9", "PS10"]:
        raise ValueError(
            f"Flow entries can only be recorded at PS1, PS8, PS9, PS10. Got {station.code}."
        )
    # Validate batch
    batch = db.query(models.Batch).filter(models.Batch.id == flow_entry.batch_id).first()
    if not batch:
        raise ValueError(f"Batch with ID {flow_entry.batch_id} not found.")
    if flow_entry.hourly_volume <= 0:
        raise ValueError("Hourly volume must be positive.")
    
    # Create flow entry
    # For receiving stations, validate that the batch is actually at the station
    if station.code in ["PS8", "PS9", "PS10"]:
        # Calculate current batch positions
        positions = get_batch_positions(db)
        batch_pos = next((p for p in positions if p.batch_id == batch.id), None)
        
        if not batch_pos:
            raise ValueError("Batch is not currently in the pipeline.")
            
        # Check if station is within batch range (trailing < station_km < leading)
        # Allow a small buffer for floating point comparisons
        station_km = station.kilometer_post
        if not (batch_pos.trailing_edge_km <= station_km <= batch_pos.leading_edge_km):
             raise ValueError(
                f"Batch {batch.name} is not at {station.code} (KM {station_km}). "
                f"Batch is at KM {batch_pos.trailing_edge_km:.2f} - {batch_pos.leading_edge_km:.2f}"
            )

    db_flow = models.FlowEntry(**flow_entry.model_dump(), entered_by=user_id)
    db.add(db_flow)
    db.commit()
    db.refresh(db_flow)
    
    # Update batch status & volume
    if station.code == "PS1":
        if batch.status == "CREATED":
            batch.status = "PUMPING"
            batch.started_pumping_at = db_flow.entry_time
        batch.pumped_volume += db_flow.hourly_volume
        if batch.pumped_volume >= batch.total_volume:
            batch.status = "COMPLETED"
            batch.finished_pumping_at = db_flow.entry_time
    
    db.commit()
    return db_flow

# ====================== VISUALIZATION ======================

def get_received_volumes(db: Session, timestamp: Optional[datetime] = None):
    received = {}
    for code in ["PS8", "PS9", "PS10"]:
        station = db.query(models.Station).filter(models.Station.code == code).first()
        if station:
            query = db.query(func.sum(models.FlowEntry.hourly_volume)).filter(
                models.FlowEntry.station_id == station.id
            )
            if timestamp:
                query = query.filter(models.FlowEntry.entry_time <= timestamp)
            
            vol = query.scalar() or 0.0
            received[code] = vol
        else:
            received[code] = 0.0
    return received

def get_batch_received_volume(db: Session, batch_id: int, timestamp: Optional[datetime] = None) -> float:
    receiving_stations = db.query(models.Station.id).filter(models.Station.code.in_(["PS8", "PS9", "PS10"])).all()
    station_ids = [s[0] for s in receiving_stations]
    
    if not station_ids:
        return 0.0

    query = db.query(func.sum(models.FlowEntry.hourly_volume)).filter(
        models.FlowEntry.batch_id == batch_id,
        models.FlowEntry.station_id.in_(station_ids)
    )
    if timestamp:
        query = query.filter(models.FlowEntry.entry_time <= timestamp)
    return query.scalar() or 0.0

def get_batch_positions(db: Session, timestamp: Optional[datetime] = None) -> List[schemas.BatchPosition]:
    LINE_CONTENT = 189.11
    ps1 = db.query(models.Station).filter(models.Station.code == "PS1").first()
    if not ps1:
        return []
    # Pre‑calculate received volumes per station (total, for pipeline physics)
    received = get_received_volumes(db, timestamp)

    def vol_to_km(injected_vol: float) -> float:
        # Segment 1: PS1 -> PS8 (0‑382 km)
        limit_s1_km = 382.0
        limit_s1_vol = limit_s1_km * LINE_CONTENT
        if injected_vol <= limit_s1_vol:
            return injected_vol / LINE_CONTENT
        # Segment 2: PS8 -> PS9 (382‑442.8 km)
        effective_after_ps8 = injected_vol - received["PS8"]
        if effective_after_ps8 <= limit_s1_vol:
            return limit_s1_km
        limit_s2_km = 442.8
        km_s2 = effective_after_ps8 / LINE_CONTENT
        if km_s2 <= limit_s2_km:
            return km_s2
        # Segment 3: PS9 -> PS10
        effective_after_ps9 = effective_after_ps8 - received["PS9"]
        return effective_after_ps9 / LINE_CONTENT

    from sqlalchemy.orm import joinedload
    
    # Filter batches based on timestamp
    query = db.query(models.Batch).options(joinedload(models.Batch.product))
    
    if timestamp:
        # Include batches that started before the timestamp
        query = query.filter(models.Batch.started_pumping_at <= timestamp)
        # And either haven't finished, or finished after the timestamp (we'll treat them as active/completed up to that point)
        # Actually, we just need batches that *started* before the timestamp. 
        # We will calculate their pumped volume up to that timestamp.
    else:
        # Default behavior: active batches
        query = query.filter(models.Batch.status.in_(["PUMPING", "COMPLETED"]))
        query = query.filter(models.Batch.started_pumping_at.isnot(None))

    batches = query.order_by(models.Batch.started_pumping_at.desc()).all()
    
    results: List[schemas.BatchPosition] = []
    injected_so_far = 0.0
    
    # We need to process batches in order of injection (oldest first) to calculate positions correctly?
    # No, the current logic iterates desc (newest first?) 
    # Wait, `injected_so_far` implies we are starting from the head of the pipeline (newest batch).
    # PS1 pushes new batches in. So the newest batch is at KM 0.
    # Yes, `started_pumping_at.desc()` gives newest first.
    
    for batch in batches:
        # Calculate pumped volume for this batch up to timestamp
        if timestamp:
            pumped_vol = (
                db.query(func.sum(models.FlowEntry.hourly_volume))
                .filter(
                    models.FlowEntry.batch_id == batch.id,
                    models.FlowEntry.station_id == ps1.id,
                    models.FlowEntry.entry_time <= timestamp
                )
                .scalar()
                or 0.0
            )
            # If pumped_vol is 0, and it started before timestamp, maybe it just started?
            # If it's 0, it effectively doesn't exist in the pipe yet or is just starting.
            if pumped_vol == 0:
                continue
        else:
            pumped_vol = batch.pumped_volume if batch.status == "PUMPING" else batch.total_volume

        batch_received = get_batch_received_volume(db, batch.id, timestamp)
        
        # Calculate positions
        # injected_so_far is the volume of batches *after* this one (newer ones)
        # Wait, if we iterate desc (newest first), then:
        # Batch 1 (Newest): starts at 0. Ends at vol_to_km(pumped_vol).
        # Batch 2 (Older): starts at vol_to_km(Batch1_vol). Ends at vol_to_km(Batch1_vol + Batch2_vol).
        
        # Current logic:
        # trailing_km = vol_to_km(injected_so_far) -> Start of this batch (closest to PS1)
        # leading_km = vol_to_km(injected_so_far + batch_vol) -> End of this batch (furthest from PS1)
        
        trailing_km = vol_to_km(injected_so_far)
        leading_km = vol_to_km(injected_so_far + pumped_vol)
        
        # Determine receiving flag
        receiving = False
        if leading_km >= 382.0 and received["PS8"] > 0:
            receiving = True
        if leading_km >= 442.8 and received["PS9"] > 0:
            receiving = True
            
        # Build BatchPosition object
        position = schemas.BatchPosition(
            batch_id=batch.id,
            batch_name=batch.name,
            product_name=batch.product.name if batch.product else "Unknown",
            color=batch.product.color if batch.product else "#000000",
            leading_edge_km=leading_km,
            trailing_edge_km=trailing_km,
            length_km=(pumped_vol / LINE_CONTENT), # Approximate length in pipe
            receiving=receiving,
            received_volume=batch_received
        )
        results.append(position)
        injected_so_far += pumped_vol
        
        if trailing_km > 450:
            break
            
    return results


def get_total_pipeline_length(db: Session) -> float:
    max_km = db.query(func.max(models.Station.kilometer_post)).scalar()
    return max_km or 450.0

# ====================== ADMIN ======================

def clear_operational_data(db: Session) -> dict:
    try:
        # Delete FlowEntries first due to foreign key constraint
        num_flows = db.query(models.FlowEntry).delete()
        
        # Delete Batches
        num_batches = db.query(models.Batch).delete()
        
        db.commit()
        return {"deleted_flow_entries": num_flows, "deleted_batches": num_batches}
    except Exception as e:
        db.rollback()
        raise e
