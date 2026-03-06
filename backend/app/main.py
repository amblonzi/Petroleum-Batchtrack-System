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
from .auth import get_current_user
from .utils import verify_password, create_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Batchtrack API",
    description="Real-time petroleum batch tracking system",
    version="2.0.0",
)

# CORS - Allow frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://linev.inphora.net",
    "https://www.linev.inphora.net",
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

# ========================= AUTH ENDPOINTS =========================
@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.User)
def get_current_user_info(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post("/auth/register", response_model=schemas.User)
def register_user(
    user: schemas.UserCreate, db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.delete("/admin/clear-data")
def clear_data(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow active users to clear data (could add role check here later)
    if not current_user.is_active:
         raise HTTPException(status_code=400, detail="Inactive user")
         
    try:
        result = crud.clear_operational_data(db)
        return {"message": "Operational data cleared successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================= VISUALIZATION ENDPOINT =========================
@app.get("/visualization/current")
def get_current_visualization(
    timestamp: Optional[datetime] = None, db: Session = Depends(get_db)
):
    ts = timestamp if timestamp is not None else datetime.utcnow()
    positions = crud.get_batch_positions(db, timestamp=ts)
    total_length = crud.get_total_pipeline_length(db)
    stations = crud.get_stations(db)
    received_vols = crud.get_received_volumes(db, timestamp=ts)

    batches = []
    for pos in positions:
        pos_dict = pos.model_dump() if hasattr(pos, "model_dump") else pos.dict()
        batches.append(
            {
                "batch_id": pos_dict["batch_id"],
                "batch_name": pos_dict["batch_name"],
                "product_name": pos_dict["product_name"],
                "color": pos_dict["color"],
                "leading_edge_km": round(pos_dict["leading_edge_km"], 2),
                "trailing_edge_km": round(pos_dict["trailing_edge_km"], 2),
                "length_km": round(pos_dict["length_km"], 2),
                "receiving": pos_dict["receiving"],
                "received_volume": round(pos_dict.get("received_volume", 0.0), 2),
            }
        )

    return {
        "timestamp": ts.isoformat(),
        "batches": batches,
        "total_pipeline_length": round(total_length, 2),
        "stations": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "kilometer_post": s.kilometer_post,
                "cumulative_volume": round(s.kilometer_post * 189.11, 2),
                "received_volume": received_vols.get(s.code, 0.0),
            }
            for s in stations
        ],
    }

# ========================= BATCH ENDPOINTS =========================
@app.post("/batches/", response_model=schemas.Batch)
def create_batch(
    batch: schemas.BatchCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.create_batch(db=db, batch=batch, user_id=current_user.id)

@app.get("/batches/", response_model=List[schemas.Batch])
def read_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_batches(db, skip=skip, limit=limit)

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

# ========================= FLOW ENTRY ENDPOINT =========================
@app.post("/flow-entries/", response_model=schemas.FlowEntry)
def create_flow_entry(
    entry: schemas.FlowEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.create_flow_entry(db=db, flow_entry=entry, user_id=current_user.id)

@app.get("/flow-entries/history", response_model=List[schemas.FlowEntry])
def get_flow_history(
    station_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return crud.get_flow_entries(db, station_id=station_id, limit=limit)

# ========================= PUBLIC DATA ENDPOINTS =========================
@app.get("/products/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.get("/stations/", response_model=List[schemas.Station])
def get_stations(db: Session = Depends(get_db)):
    return crud.get_stations(db)

# ========================= HEALTH & ROOT =========================
@app.get("/")
def root():
    return {
        "message": "Kenya Pipeline Batch Tracker API",
        "docs": "https://api.linev.inphora.net/docs",
        "frontend": "https://linev.inphora.net",
    }

@app.get("/health")
def health():
    return {"status": "OK", "time": datetime.utcnow().isoformat() + "Z"}