import os
import sys

# Add the current directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Batch, FlowEntry, Base
from sqlalchemy import text

def clear_data():
    db = SessionLocal()
    try:
        print("Clearing operational data...")
        
        # Delete FlowEntries first due to foreign key constraint
        num_flows = db.query(FlowEntry).delete()
        print(f"Deleted {num_flows} flow entries.")
        
        # Delete Batches
        num_batches = db.query(Batch).delete()
        print(f"Deleted {num_batches} batches.")
        
        db.commit()
        print("Database cleared successfully (Users, Products, Stations preserved).")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
