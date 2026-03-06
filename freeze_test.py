import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8001/api"

def get_token():
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": "admin",
        "password": "admin123"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())["access_token"]

def create_batch(token, name, product_id):
    url = f"{BASE_URL}/batches/"
    data = json.dumps({
        "name": name,
        "product_id": product_id,
        "total_volume": 100000
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def create_flow(token, batch_id, station_id, volume):
    url = f"{BASE_URL}/flow-entries/"
    data = json.dumps({
        "batch_id": batch_id,
        "station_id": station_id,
        "hourly_volume": volume,
        "entry_time": "2024-11-24T10:00:00Z" # Fixed time for simplicity
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def get_visualization(token):
    url = f"{BASE_URL}/visualization/current"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def get_station_id(token, code):
    url = f"{BASE_URL}/stations/"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as response:
        stations = json.loads(response.read().decode())
        for s in stations:
            if s["code"] == code:
                return s["id"]
    return None

def run_test():
    try:
        token = get_token()
        print("✓ Login successful")
        
        ps1_id = get_station_id(token, "PS1")
        ps8_id = get_station_id(token, "PS8")
        print(f"✓ Found Stations: PS1={ps1_id}, PS8={ps8_id}")
        
        # Create Batch
        batch = create_batch(token, "FREEZE-TEST-BATCH", 1) # 1 = PMS
        print(f"✓ Created Batch: {batch['name']}")
        
        # 1. Push Batch past PS8 (Need > 72,240 m3)
        # We pump 80,000 m3 at PS1
        print("✓ Pumping 80,000 m3 at PS1 to push batch downstream...")
        create_flow(token, batch['id'], ps1_id, 80000)
        
        viz = get_visualization(token)
        batch_pos = next(b for b in viz['batches'] if b['batch_id'] == batch['id'])
        print(f"  Position after push: {batch_pos['leading_edge_km']:.2f} km (Should be > 382)")
        
        initial_km = batch_pos['leading_edge_km']
        
        # 2. Test Freeze: Pump at PS1 AND Receive at PS8
        print("✓ Pumping 1,000 m3 at PS1 AND Receiving 1,000 m3 at PS8...")
        create_flow(token, batch['id'], ps1_id, 1000)
        create_flow(token, batch['id'], ps8_id, 1000)
        
        viz = get_visualization(token)
        batch_pos = next(b for b in viz['batches'] if b['batch_id'] == batch['id'])
        final_km = batch_pos['leading_edge_km']
        
        print(f"  Position after freeze test: {final_km:.2f} km")
        
        diff = final_km - initial_km
        print(f"  Movement: {diff:.4f} km")
        
        if diff < 0.1:
            print("✓ SUCCESS: Batch did not move significantly (Frozen downstream of PS8)")
        else:
            print("❌ FAILURE: Batch moved significantly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
