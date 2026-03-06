import sys
import os

# Add the backend directory to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

try:
    from app import crud
    from app.database import SessionLocal
    
    print("Successfully imported app.crud")
    
    db = SessionLocal()
    try:
        print("Testing get_batch_positions...")
        positions = crud.get_batch_positions(db)
        print(f"Success. Found {len(positions)} batches.")
    except Exception as e:
        print(f"Error calling get_batch_positions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

except Exception as e:
    print(f"Import Error: {e}")
    import traceback
    traceback.print_exc()
