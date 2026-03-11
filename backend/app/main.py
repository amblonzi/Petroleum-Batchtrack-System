# backend/app/main.py

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from . import crud, models, schemas
from .database import engine, get_db
from .config import settings
from .auth import get_current_user, get_current_admin_user
from .utils import verify_password, create_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BatchtrackOS API",
    description="KPC Multi-Line Petroleum Batch Tracking System",
    version="3.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://linev.inphora.net",
    "https://www.linev.inphora.net",
    "https://batchtrackos.inphora.net",
    "http://batchtrackos.inphora.net",
]
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    origins.extend(env_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _resolve_pipeline(line: str, db: Session) -> models.Pipeline:
    pipeline = crud.get_pipeline_by_line(db, line)
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline '{line}' not found.")
    return pipeline


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.User)
def get_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


# ── Admin ─────────────────────────────────────────────────────────────────────
@app.delete("/admin/clear-data")
def clear_data(current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return crud.clear_operational_data(db)

@app.get("/admin/users", response_model=List[schemas.User])
def admin_get_users(current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.post("/admin/users", response_model=schemas.User)
def admin_create_user(user: schemas.UserCreate, current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.put("/admin/users/{user_id}/role", response_model=schemas.User)
def admin_update_user_role(user_id: int, is_admin: bool, current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role.")
    user = crud.update_user_role(db, user_id, is_admin)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success"}

@app.put("/admin/pipelines/{pipeline_id}", response_model=schemas.Pipeline)
def admin_update_pipeline(pipeline_id: int, pipeline_update: schemas.PipelineUpdate, current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    pipeline = crud.update_pipeline(db, pipeline_id, pipeline_update)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@app.delete("/admin/pipelines/{pipeline_id}/data")
def admin_clear_pipeline_data(pipeline_id: int, current_admin = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    pipeline = crud.get_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return crud.clear_pipeline_data(db, pipeline_id)



# ── Pipelines ─────────────────────────────────────────────────────────────────
@app.get("/pipelines/", response_model=List[schemas.Pipeline])
def get_pipelines(db: Session = Depends(get_db)):
    return crud.get_pipelines(db)


# ── Visualization ─────────────────────────────────────────────────────────────
@app.get("/visualization/current")
def get_visualization(
    line: str = "L5",
    timestamp: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    pipeline = _resolve_pipeline(line, db)
    ts = timestamp if timestamp is not None else datetime.utcnow()
    positions = crud.get_batch_positions(db, pipeline_id=pipeline.id, timestamp=ts)
    received_vols = crud.get_received_volumes_for_api(db, pipeline_id=pipeline.id, timestamp=ts)
    stations = crud.get_stations(db, pipeline_id=pipeline.id)

    batches = []
    for pos in positions:
        pd = pos.model_dump()
        batches.append({
            "batch_id": pd["batch_id"],
            "batch_name": pd["batch_name"],
            "product_name": pd["product_name"],
            "color": pd["color"],
            "leading_edge_km": round(pd["leading_edge_km"], 2),
            "trailing_edge_km": round(pd["trailing_edge_km"], 2),
            "length_km": round(pd["length_km"], 2),
            "receiving": pd["receiving"],
            "received_volume": round(pd.get("received_volume", 0.0), 2),
        })

    return {
        "timestamp": ts.isoformat(),
        "line_number": pipeline.line_number,
        "line_name": pipeline.name,
        "line_fill_rate": pipeline.line_fill_rate,
        "batches": batches,
        "total_pipeline_length": round(pipeline.total_length_km, 2),
        "stations": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "kilometer_post": s.kilometer_post,
                "station_type": s.station_type,
                "pipeline_id": s.pipeline_id,
                "cumulative_volume": round(s.kilometer_post * pipeline.line_fill_rate, 2),
                "received_volume": received_vols.get(s.id, 0.0),
            }
            for s in stations
        ],
    }


# ── Batches ───────────────────────────────────────────────────────────────────
@app.post("/batches/", response_model=schemas.Batch)
def create_batch(
    batch: schemas.BatchCreate,
    line: str = "L5",
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    pipeline = _resolve_pipeline(line, db)
    return crud.create_batch(db=db, batch=batch, pipeline_id=pipeline.id, user_id=current_user.id)


@app.get("/batches/", response_model=List[schemas.Batch])
def read_batches(line: str = "L5", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pipeline = _resolve_pipeline(line, db)
    batches = crud.get_batches(db, pipeline_id=pipeline.id, skip=skip, limit=limit)
    
    # Populate received_volume for each batch
    for b in batches:
        b.received_volume = crud.get_batch_received_volume(db, batch_id=b.id, pipeline_id=pipeline.id)
        
    return batches


@app.put("/batches/{batch_id}", response_model=schemas.Batch)
def update_batch(
    batch_id: int,
    batch: schemas.BatchCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_batch = crud.update_batch(db, batch_id=batch_id, batch_update=batch)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch


@app.delete("/batches/{batch_id}")
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    if not crud.delete_batch(db, batch_id=batch_id):
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"status": "success"}


# ── Flow Entries ──────────────────────────────────────────────────────────────
@app.post("/flow-entries/", response_model=schemas.FlowEntry)
def create_flow_entry(
    entry: schemas.FlowEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    try:
        return crud.create_flow_entry(db=db, flow_entry=entry, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/flow-entries/history", response_model=List[schemas.FlowEntry])
def get_flow_history(
    line: str = "L5",
    station_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    pipeline = _resolve_pipeline(line, db)
    return crud.get_flow_entries(db, station_id=station_id, pipeline_id=pipeline.id, limit=limit)


# ── Public Data ───────────────────────────────────────────────────────────────
@app.get("/products/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)


@app.get("/stations/", response_model=List[schemas.Station])
def get_stations(line: str = "L5", db: Session = Depends(get_db)):
    pipeline = _resolve_pipeline(line, db)
    return crud.get_stations(db, pipeline_id=pipeline.id)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "BatchtrackOS API — KPC Multi-Product Pipeline (MPP) Tracker",
        "version": "3.0.0",
        "pipelines": "GET /pipelines/",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "OK", "time": datetime.utcnow().isoformat() + "Z"}