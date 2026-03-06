import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import crud
from datetime import datetime

def reproduce():
    db = SessionLocal()
    try:
        print("Calling get_current_visualization logic...")
        ts = datetime.utcnow()
        # Mocking what main.py does
        positions = crud.get_batch_positions(db, timestamp=ts)
        print(f"Positions: {positions}")
        
        total_length = crud.get_total_pipeline_length(db)
        print(f"Total Length: {total_length}")
        
        stations = crud.get_stations(db)
        print(f"Stations: {len(stations)}")
        
        received_vols = crud.get_received_volumes(db, timestamp=ts)
        print(f"Received Vols: {received_vols}")

    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
