import sys
sys.path.insert(0, 'C:/Users/Evans/Desktop/Batchtrack')

from backend.app.database import SessionLocal
from backend.app.main import get_current_visualization

db = SessionLocal()
try:
    print("Testing get_current_visualization endpoint function...")
    result = get_current_visualization(db=db)
    print(f"✓ Success!")
    print(f"  Timestamp: {result['timestamp']}")
    print(f"  Total batches: {len(result['batches'])}")
    print(f"  Total stations: {len(result['stations'])}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
