
import urllib.request
import urllib.parse
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def get_access_token():
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": "admin",
        "password": "admin123"
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_receiving_logic():
    token = get_access_token()
    if not token:
        return

    # 1. Get current visualization to find a batch and its position
    print("Fetching pipeline state...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/visualization/current?line=L5", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to get visualization: {e}")
        return

    batches = data['batches']
    stations = data['stations']
    
    ps8 = next((s for s in stations if s['code'] == 'PS8'), None)
    if not ps8:
        print("PS8 not found")
        return

    print(f"PS8 Location: {ps8['kilometer_post']} km")

    # Find a batch that is NOT at PS8
    batch_not_at_ps8 = None
    for b in batches:
        if not (b['trailing_edge_km'] <= ps8['kilometer_post'] <= b['leading_edge_km']):
            batch_not_at_ps8 = b
            break
    
    if batch_not_at_ps8:
        print(f"Testing invalid receipt for Batch {batch_not_at_ps8['batch_id']} at PS8...")
        payload = {
            "batch_id": batch_not_at_ps8['batch_id'],
            "station_id": ps8['id'],
            "hourly_volume": 100.0,
            "entry_time": datetime.utcnow().isoformat()
        }
        
        req = urllib.request.Request(
            f"{BASE_URL}/flow-entries/",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        
        try:
            with urllib.request.urlopen(req) as res:
                print(f"❌ Failed: Should have been blocked but got {res.status}")
        except urllib.error.HTTPError as e:
            if e.code == 500 or e.code == 400:
                print(f"✓ Correctly blocked: {e.read().decode()}")
            else:
                print(f"❌ Unexpected error code: {e.code}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    else:
        print("Could not find a batch NOT at PS8 to test invalid receipt.")

if __name__ == "__main__":
    test_receiving_logic()
