"""
init_db.py — Seed all KPC pipeline lines with exact station data.

Km posts are derived from: km = cumulative_volume / line_fill_rate

Line 2: 34.83 m³/km  |  Line 3: 20.25 m³/km  |  Line 4: 52.68 m³/km
Line 5: 189.11 m³/km |  Line 6: 20.25 m³/km
"""
from app.database import SessionLocal, engine
from app import models, schemas
from app.crud import create_user, create_product, create_pipeline, create_station, create_batch, create_flow_entry
from app.utils import get_password_hash
from datetime import datetime, timezone, timedelta


# ── Per-line station data (km = vol / line_fill_rate) ─────────────────────────
# Line 2: Nairobi → Eldoret, 14-inch, 34.83 m³/km
L2_FILL = 34.83
L2_STATIONS = [
    {"code": "PS21",  "name": "Nairobi",       "vol": 0.0,    "type": "lifting"},
    {"code": "PS22",  "name": "Ngema",          "vol": 2250.0, "type": "intermediate"},
    {"code": "PS23",  "name": "Morendat",       "vol": 4417.0, "type": "intermediate"},
    {"code": "PS25",  "name": "Nakuru Depot",   "vol": 5904.0, "type": "intermediate"},
    {"code": "PS24",  "name": "Nakuru Soilo",   "vol": 6444.0, "type": "intermediate"},
    {"code": "PS26",  "name": "Sinendet",       "vol": 7826.0, "type": "intermediate"},
    {"code": "PS26A", "name": "T.P.",           "vol": 9850.0, "type": "intermediate"},
    {"code": "PS27",  "name": "Eldoret",        "vol": 10803.0,"type": "receiving"},
]

# Line 3: Sinendet → Kisumu, 6-inch, 20.25 m³/km
L3_FILL = 20.25
L3_STATIONS = [
    {"code": "PS26",  "name": "Sinendet",       "vol": 0.0,    "type": "lifting"},
    {"code": "PS28",  "name": "Kisumu",         "vol": 2470.0, "type": "receiving"},
]

# Line 4: Nairobi → Eldoret, 10-inch, 52.68 m³/km  (runs parallel to Line 2)
L4_FILL = 52.68
L4_STATIONS = [
    {"code": "PS21",  "name": "Nairobi",       "vol": 0.0,      "type": "lifting"},
    {"code": "PS22",  "name": "Ngema",          "vol": 6571.7,   "type": "intermediate"},
    {"code": "PS23",  "name": "Morendat",       "vol": 11678.9,  "type": "intermediate"},
    {"code": "PS25",  "name": "Nakuru Depot",   "vol": 15711.0,  "type": "intermediate"},
    {"code": "PS24",  "name": "Nakuru Soilo",   "vol": 17147.7,  "type": "intermediate"},
    {"code": "PS26",  "name": "Sinendet",       "vol": 20734.8,  "type": "intermediate"},
    # PS26A data for Line 4 not available (likely data omission); skipped
    {"code": "PS27",  "name": "Eldoret",        "vol": 30170.6,  "type": "receiving"},
]

# Line 5: Mombasa → Nairobi (existing), 14-inch, 189.11 m³/km
L5_FILL = 189.11
L5_STATIONS = [
    {"code": "PS1",  "name": "Mombasa",                 "vol": 0.0,     "type": "lifting"},
    {"code": "PS2",  "name": "Station 2",               "vol": 10393.0, "type": "intermediate"},
    {"code": "PS3",  "name": "Station 3",               "vol": 20802.1, "type": "intermediate"},
    {"code": "PS4",  "name": "Station 4",               "vol": 32870.9, "type": "intermediate"},
    {"code": "PS5",  "name": "Station 5",               "vol": 43686.8, "type": "intermediate"},
    {"code": "PS6",  "name": "Station 6",               "vol": 53380.2, "type": "intermediate"},
    {"code": "PS7",  "name": "Station 7",               "vol": 64313.6, "type": "intermediate"},
    {"code": "PS8",  "name": "Konza",                   "vol": 72238.0, "type": "receiving"},
    {"code": "PS9",  "name": "Receiving Station 9",     "vol": 83748.7, "type": "receiving"},
    {"code": "PS10", "name": "Embakasi (Nairobi)",      "vol": 84965.0, "type": "receiving"},
]

# Line 6: Sinendet → Kisumu, 10-inch, 20.25 m³/km  (parallel to Line 3)
L6_FILL = 20.25
L6_STATIONS = [
    {"code": "PS26",  "name": "Sinendet",       "vol": 0.0,    "type": "lifting"},
    {"code": "PS28",  "name": "Kisumu",         "vol": 2470.0, "type": "receiving"},
]


PIPELINES = [
    {
        "line_number": "L2",
        "name": "Line 2 — Nairobi to Eldoret",
        "description": "14-inch main western pipeline, Nairobi to Eldoret via Nakuru",
        "fill": L2_FILL,
        "stations": L2_STATIONS,
    },
    {
        "line_number": "L3",
        "name": "Line 3 — Sinendet to Kisumu",
        "description": "6-inch pipeline, Sinendet to Kisumu port",
        "fill": L3_FILL,
        "stations": L3_STATIONS,
    },
    {
        "line_number": "L4",
        "name": "Line 4 — Nairobi to Eldoret",
        "description": "10-inch parallel western pipeline, Nairobi to Eldoret",
        "fill": L4_FILL,
        "stations": L4_STATIONS,
    },
    {
        "line_number": "L5",
        "name": "Line 5 — Mombasa to Nairobi",
        "description": "14-inch main trunk pipeline, Changamwe to Embakasi (449 km)",
        "fill": L5_FILL,
        "stations": L5_STATIONS,
    },
    {
        "line_number": "L6",
        "name": "Line 6 — Sinendet to Kisumu",
        "description": "10-inch parallel pipeline, Sinendet to Kisumu",
        "fill": L6_FILL,
        "stations": L6_STATIONS,
    },
]


def init_database():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(models.User).count() > 0:
            print("Database already initialized. Delete it and re-run to reinitialize.")
            return

        print("=" * 60)
        print("BatchtrackOS — Initializing Multi-Line Pipeline Database")
        print("=" * 60)

        # Admin user
        user = create_user(db, schemas.UserCreate(
            username="admin", password="admin123", full_name="System Administrator"
        ))
        print(f"✓ User: {user.username}")

        # Products
        products_data = [
            {"code": "PMS", "name": "Premium Motor Spirit", "color": "#e53e3e"},
            {"code": "AGO", "name": "Automotive Gas Oil",   "color": "#1a1a1a"},
            {"code": "DPK", "name": "Dual Purpose Kerosene","color": "#3182ce"},
        ]
        products = {}
        for pd in products_data:
            p = create_product(db, schemas.ProductCreate(**pd))
            products[p.code] = p
            print(f"✓ Product: {p.name}")

        print()

        # Pipelines and stations
        pipeline_objects = {}
        for pl_data in PIPELINES:
            fill = pl_data["fill"]
            station_defs = pl_data["stations"]
            total_km = station_defs[-1]["vol"] / fill  # last station vol → total length

            pipeline = create_pipeline(db, schemas.PipelineCreate(
                line_number=pl_data["line_number"],
                name=pl_data["name"],
                description=pl_data["description"],
                total_length_km=round(total_km, 2),
                line_fill_rate=fill,
                is_active=True,
            ))
            pipeline_objects[pipeline.line_number] = pipeline

            print(f"✓ {pipeline.line_number}: {pipeline.name}")
            print(f"  Fill rate: {fill} m³/km  |  Length: {pipeline.total_length_km:.2f} km")

            for st in station_defs:
                km = round(st["vol"] / fill, 2)
                create_station(db, schemas.StationCreate(
                    code=st["code"],
                    name=st["name"],
                    kilometer_post=km,
                    station_type=st["type"],
                    pipeline_id=pipeline.id,
                ))
                marker = "🟢" if st["type"] == "lifting" else ("🔵" if st["type"] == "receiving" else "·")
                print(f"  {marker} {st['code']:6} {km:7.2f} km  —  {st['name']}")
            print()

        # Sample batches for Line 5 to show the demo
        l5 = pipeline_objects["L5"]
        sample_batches = [
            {"name": "AGO-2026-001", "product_code": "AGO", "vol": 10000.0, "hours": 95},
            {"name": "PMS-2026-001", "product_code": "PMS", "vol": 8000.0,  "hours": 57},
            {"name": "DPK-2026-001", "product_code": "DPK", "vol": 5000.0,  "hours": 28},
        ]

        lifting = db.query(models.Station).filter(
            models.Station.pipeline_id == l5.id,
            models.Station.station_type == "lifting"
        ).first()

        base_time = datetime(2026, 1, 10, 6, 0, 0, tzinfo=timezone.utc)
        for i, sb in enumerate(sample_batches):
            b = create_batch(db, schemas.BatchCreate(
                name=sb["name"],
                product_id=products[sb["product_code"]].id,
                total_volume=sb["vol"],
            ), pipeline_id=l5.id, user_id=user.id)

            t0 = base_time + timedelta(days=i)
            for h in range(sb["hours"]):
                create_flow_entry(db, schemas.FlowEntryCreate(
                    batch_id=b.id,
                    station_id=lifting.id,
                    entry_time=t0 + timedelta(hours=h),
                    hourly_volume=500.0,
                ), user_id=user.id)

            print(f"✓ L5 demo batch: {b.name}  ({sb['hours']} flow entries)")

        print()
        print("=" * 60)
        print("INITIALIZATION COMPLETE")
        print(f"  Pipelines: {len(PIPELINES)}")
        print(f"  Login: admin / admin123")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback; traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()