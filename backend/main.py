from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from . import crud, models, schemas, auth
from .database import SessionLocal, engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LINEV Pipeline Batch Tracker")

# CORS – allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ────────────────────────── AUTH ──────────────────────────
@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# ─────────────────────── VISUALIZATION ───────────────────────
@app.get("/api/visualization/current", response_model=schemas.BatchVisualization)
def get_current_visualization(db: Session = Depends(get_db)):
    positions = crud.get_batch_positions(db)
    total_length = crud.get_total_pipeline_length(db)
    stations = crud.get_stations(db)

    batches = []
    for pos in positions:
        length_km = pos.total_volume / 189.11
        batches.append(schemas.BatchPosition(
            batch_id=pos.batch_id,
            batch_name=pos.batch_name,
            product_name=pos.product_name,
            color=pos.color,
            leading_edge_km=round(pos.leading_edge_km, 2),
            trailing_edge_km=round(pos.trailing_edge_km, 2),
            length_km=round(length_km, 2)
        ))

    return schemas.BatchVisualization(
        timestamp=crud.get_db().execute("SELECT now()").scalar(),
        batches=batches,
        total_pipeline_length=total_length,
        stations=[schemas.Station(**s.__dict__) for s in stations]
    )

# ─────────────────────── PROTECTED ROUTES ───────────────────────
@app.post("/api/batches/", response_model=schemas.Batch)
def create_batch(
    batch: schemas.BatchCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.create_batch(db=db, batch=batch, user_id=current_user.id)

@app.post("/api/flow-entries/", response_model=schemas.FlowEntry)
def create_flow_entry(
    entry: schemas.FlowEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.create_flow_entry(db=db, flow_entry=entry, user_id=current_user.id)

# Public routes (for dropdowns)
@app.get("/api/products/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return crud.get_products(db)

@app.get("/api/stations/", response_model=List[schemas.station])
def read_stations(db: Session = Depends(get_db)):
    return crud.get_stations(db)

# Optional: simple protected home
@app.get("/")
def root():
    return {"message": "Kenya Pipeline Tracker API – go to /docs"}