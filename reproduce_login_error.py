
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.database import SessionLocal
from backend.app import crud, auth, utils, schemas
from backend.app.config import settings

def test_login():
    db = SessionLocal()
    try:
        # Create a test user if not exists
        username = "testuser"
        password = "password123"
        user = crud.get_user_by_username(db, username)
        if not user:
            print(f"Creating user {username}...")
            crud.create_user(db, schemas.UserCreate(username=username, password=password, full_name="Test User"))
            user = crud.get_user_by_username(db, username)
        
        print(f"Found user: {user.username}")
        
        # Test password verification
        print("Verifying password...")
        is_valid = utils.verify_password(password, user.password_hash)
        print(f"Password valid: {is_valid}")
        
        # Test token creation
        print("Creating access token...")
        from datetime import timedelta
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = utils.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        print(f"Token created: {access_token[:20]}...")
        
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login()
