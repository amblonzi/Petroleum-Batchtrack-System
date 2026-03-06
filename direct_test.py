import sys
sys.path.insert(0, 'C:/Users/Evans/Desktop/Batchtrack')

from backend.app.database import SessionLocal
from backend.app import crud

db = SessionLocal()
try:
    print("Testing get_batch_positions...")
    positions = crud.get_batch_positions(db)
    print(f"✓ Success! Got {len(positions)} batch positions")
    for pos in positions:
        print(f"  - Batch {pos.batch_id}: {pos.batch_name} at {pos.leading_edge_km:.2f} km")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
