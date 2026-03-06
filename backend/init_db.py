from app.database import SessionLocal, engine
from app import models, schemas
from app.crud import create_user, create_product, create_station, create_batch, create_flow_entry
from app.utils import get_password_hash
from datetime import datetime, timezone, timedelta

def init_database():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(models.User).count() > 0:
            print("Database already initialized!")
            print("\nTo reinitialize, delete the database file and run again:")
            print("  Remove-Item pipeline_tracker.db")
            print("  uv run python init_db.py")
            return
        
        print("Initializing database with pipeline structure...")
        print("="*60)
        
        # Create first user
        user = create_user(db, schemas.UserCreate(
            username="admin",
            password="admin123",
            full_name="System Administrator"
        ))
        print(f"✓ Created user: {user.username}")
        
        # Create products with realistic colors
        products_data = [
            {"code": "MSP", "name": "Premium Motor Spirit (Petrol)", "color": "#FF0000"}, # Red
            {"code": "AGO", "name": "Automotive Gas Oil (Diesel)", "color": "#000000"},   # Black
            {"code": "JET A1", "name": "Jet Fuel A1", "color": "#00FF00"},               # Green
            {"code": "IK", "name": "Illuminating Kerosene", "color": "#0000FF"},         # Blue
        ]
        
        products = []
        for prod_data in products_data:
            product = create_product(db, schemas.ProductCreate(**prod_data))
            products.append(product)
            print(f"✓ Created product: {product.name} ({product.color})")
        
        # Create stations along the actual pipeline
        # Total Distance: 449.19 km
        # Average Line Content: 189.11 m³/km
        stations_data = [
            {"code": "PS1", "name": "Lifting Station", "kilometer_post": 0.0},
            {"code": "PS2", "name": "Station 2", "kilometer_post": 54.97},
            {"code": "PS3", "name": "Station 3", "kilometer_post": 110.0},
            {"code": "PS4", "name": "Station 4", "kilometer_post": 173.78},
            {"code": "PS5", "name": "Station 5", "kilometer_post": 231.02},
            {"code": "PS6", "name": "Station 6", "kilometer_post": 282.35},
            {"code": "PS7", "name": "Station 7", "kilometer_post": 340.11},
            {"code": "PS8", "name": "Receiving Station 8", "kilometer_post": 382.0},
            {"code": "PS9", "name": "Receiving Station 9", "kilometer_post": 442.8},
            {"code": "PS10", "name": "Receiving Station 10", "kilometer_post": 449.19},
        ]
        
        stations = []
        print("\n" + "="*60)
        print("PIPELINE CONFIGURATION")
        print("="*60)
        print(f"Total Distance: 449.19 km")
        print(f"Average Line Content: 189.11 m³/km")
        print(f"Total Pipeline Capacity: {449.19 * 189.11:.2f} m³")
        print("="*60)
        print("\nSTATIONS:")
        print("-"*60)
        
        for station_data in stations_data:
            station = create_station(db, schemas.StationCreate(**station_data))
            stations.append(station)
            station_type = ""
            if "Lifting" in station.name:
                station_type = "🟢 LIFTING"
            elif "Receiving" in station.name:
                station_type = " RECEIVING"
            else:
                station_type = "🟡 INTERMEDIATE"
            
            print(f"{station_type:20} {station.code:6} @ {station.kilometer_post:7.2f} km - {station.name}")
        
        print("="*60)
        
        # Create sample batches with realistic volumes
        batches_data = [
            {
                "name": "BATCH-2024-001-MSP",
                "product_id": products[0].id,  # MSP
                "total_volume": 8000.0,  # 8000 m³
                "started_pumping_at": datetime(2024, 11, 15, 6, 0, 0, tzinfo=timezone.utc)
            },
            {
                "name": "BATCH-2024-002-AGO",
                "product_id": products[1].id,  # AGO
                "total_volume": 10000.0,  # 10000 m³
                "started_pumping_at": datetime(2024, 11, 16, 8, 0, 0, tzinfo=timezone.utc)
            },
            {
                "name": "BATCH-2024-003-IK",
                "product_id": products[2].id,  # IK
                "total_volume": 5000.0,  # 5000 m³
                "started_pumping_at": datetime(2024, 11, 17, 10, 0, 0, tzinfo=timezone.utc)
            },
            {
                "name": "BATCH-2024-004-JET",
                "product_id": products[3].id,  # JET A1
                "total_volume": 6000.0,  # 6000 m³
                "started_pumping_at": datetime(2024, 11, 18, 7, 0, 0, tzinfo=timezone.utc)
            }
        ]
        
        batches = []
        print("\nBATCHES CREATED:")
        print("-"*60)
        for batch_data in batches_data:
            batch = create_batch(db, schemas.BatchCreate(**batch_data), user_id=user.id)
            batches.append(batch)
            product_name = next(p.name for p in products if p.id == batch.product_id)
            batch_length_km = batch.total_volume / 189.11
            print(f"✓ {batch.name}")
            print(f"  Product: {product_name}")
            print(f"  Volume: {batch.total_volume:,.0f} m³ ({batch_length_km:.2f} km length)")
            # Handle case where started_pumping_at might be None (though in this seed data it is set)
            started_str = batch.started_pumping_at.strftime('%Y-%m-%d %H:%M') if batch.started_pumping_at else "Not Started"
            print(f"  Started: {started_str}")
            print()
        
        # Create sample flow entries to simulate batches at different positions
        print("="*60)
        print("SIMULATING FLOW ENTRIES (Batch Movement)")
        print("="*60)
        
        flow_entries_data = []
        
        # Batch 1 - MSP (Well advanced - around 250 km into pipeline)
        # To reach 250 km: 250 * 189.11 = 47,277.5 m³ pumped
        # Total volume 8000 m³, need to pump 47,277.5 m³ at ~500 m³/hour
        for hour in range(95):  # 95 hours of pumping
            flow_entries_data.append({
                "batch_id": batches[0].id,
                "station_id": stations[0].id,  # PS1
                "entry_time": datetime(2024, 11, 15, 6, 0, 0, tzinfo=timezone.utc) + timedelta(hours=hour),
                "hourly_volume": 500.0
            })
        
        # Batch 2 - AGO (Mid-pipeline - around 150 km)
        # To reach 150 km: 150 * 189.11 = 28,366.5 m³ pumped
        for hour in range(57):  # 57 hours
            flow_entries_data.append({
                "batch_id": batches[1].id,
                "station_id": stations[0].id,
                "entry_time": datetime(2024, 11, 16, 8, 0, 0, tzinfo=timezone.utc) + timedelta(hours=hour),
                "hourly_volume": 500.0
            })
        
        # Batch 3 - IK (Early pipeline - around 75 km)
        # To reach 75 km: 75 * 189.11 = 14,183.25 m³ pumped
        for hour in range(28):  # 28 hours
            flow_entries_data.append({
                "batch_id": batches[2].id,
                "station_id": stations[0].id,
                "entry_time": datetime(2024, 11, 17, 10, 0, 0, tzinfo=timezone.utc) + timedelta(hours=hour),
                "hourly_volume": 500.0
            })
        
        # Batch 4 - JET (Just started - around 20 km)
        # To reach 20 km: 20 * 189.11 = 3,782.2 m³ pumped
        for hour in range(8):  # 8 hours
            flow_entries_data.append({
                "batch_id": batches[3].id,
                "station_id": stations[0].id,
                "entry_time": datetime(2024, 11, 18, 7, 0, 0, tzinfo=timezone.utc) + timedelta(hours=hour),
                "hourly_volume": 500.0
            })
        
        for flow_data in flow_entries_data:
            create_flow_entry(db, schemas.FlowEntryCreate(**flow_data), user_id=user.id)
        
        print(f"✓ Created {len(flow_entries_data)} flow entries")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print(f"\n📊 Pipeline Configuration:")
        print(f"   • Total Length: 449.19 km")
        print(f"   • Line Content: 189.11 m³/km")
        print(f"   • Stations: 10 (1 lifting, 3 receiving, 6 intermediate)")
        print(f"   • Products: 4")
        print(f"   • Active Batches: 4")
        print(f"   • Flow Entries: {len(flow_entries_data)}")
        
        print(f"\n🔐 Login Credentials:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
        print(f"\n🌐 API Documentation:")
        print(f"   http://localhost:8000/docs")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()