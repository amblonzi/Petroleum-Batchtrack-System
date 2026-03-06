import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8001/api"

# Get token
url = f"{BASE_URL}/auth/login"
data = urllib.parse.urlencode({
    "username": "admin",
    "password": "admin123"
}).encode()
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
with urllib.request.urlopen(req) as response:
    token = json.loads(response.read().decode())["access_token"]
    print(f"✓ Login successful, token: {token[:20]}...")

# Create batch
url = f"{BASE_URL}/batches/"
data = json.dumps({
    "name": "TEST-BATCH",
    "product_id": 1,
    "total_volume": 5000
}).encode()
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req) as response:
        batch = json.loads(response.read().decode())
        print(f"✓ Created batch: {batch['name']}, ID: {batch['id']}")
except Exception as e:
    print(f"❌ Error creating batch: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Create flow entry
url = f"{BASE_URL}/flow-entries/"
data = json.dumps({
    "batch_id": batch['id'],
    "station_id": 1,  # PS1
    "hourly_volume": 1000.0,
    "entry_time": "2024-11-24T10:00:00Z"
}).encode()
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req) as response:
        flow = json.loads(response.read().decode())
        print(f"✓ Created flow entry: {flow['id']}")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    print(f"Response: {e.read().decode()}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error creating flow entry: {e}")
    import traceback
    traceback.print_exc()
