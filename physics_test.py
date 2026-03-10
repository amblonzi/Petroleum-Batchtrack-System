import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        raise

def get_token():
    # Use form-urlencoded for login
    data = "username=admin&password=admin123".encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, method="POST")
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))["access_token"]

def create_batch(token, name, product_id, volume):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "pipeline_id": 4, # L5 Pipeline
        "name": name,
        "product_id": product_id,
        "total_volume": volume
    }
    return make_request(f"{BASE_URL}/batches/?line=L5", method="POST", data=data, headers=headers)

def pump_batch(token, batch_id, volume):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "batch_id": batch_id,
        "station_id": 15, # PS1 for L5
        "hourly_volume": volume,
        "entry_time": datetime.utcnow().isoformat() + "Z"
    }
    return make_request(f"{BASE_URL}/flow-entries/", method="POST", data=data, headers=headers)

def get_viz(token):
    headers = {"Authorization": f"Bearer {token}"}
    return make_request(f"{BASE_URL}/visualization/current?line=L5", method="GET", headers=headers)

def run_test():
    try:
        token = get_token()
        
        # 1. Create Batch A (Old)
        print("Creating Batch A...")
        batch_a = create_batch(token, "PHYSICS-TEST-A", 1, 1000)
        
        # 2. Pump Batch A (Start it)
        print("Pumping Batch A...")
        pump_batch(token, batch_a["id"], 100)
        
        # 3. Create Batch B (New)
        print("Creating Batch B...")
        batch_b = create_batch(token, "PHYSICS-TEST-B", 2, 1000)
        
        # 4. Pump Batch B (Start it - pushes A)
        print("Pumping Batch B...")
        pump_batch(token, batch_b["id"], 100)
        
        # 5. Pump Batch A AGAIN (The anomaly)
        print("Pumping Batch A AGAIN (Should be impossible physically)...")
        pump_batch(token, batch_a["id"], 100)
        
        # 6. Check Visualization
        viz = get_viz(token)
        
        # Find positions
        pos_a = next(b for b in viz["batches"] if b["batch_id"] == batch_a["id"])
        pos_b = next(b for b in viz["batches"] if b["batch_id"] == batch_b["id"])
        
        print("\nVisualization Results:")
        print(f"Batch B (Newer): {pos_b['leading_edge_km']:.2f} km to {pos_b['trailing_edge_km']:.2f} km")
        print(f"Batch A (Older): {pos_a['leading_edge_km']:.2f} km to {pos_a['trailing_edge_km']:.2f} km")
        
        if pos_b['trailing_edge_km'] == 0:
            print("\nAnomaly Confirmed: Batch B is at PS1, but we just pumped Batch A.")
            print("We effectively injected Batch A downstream, skipping Batch B.")
        else:
            print("\nSomething else happened.")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    run_test()
