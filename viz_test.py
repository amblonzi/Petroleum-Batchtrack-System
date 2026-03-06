import urllib.request
import json

BASE_URL = "http://127.0.0.1:8001/api"

try:
    url = f"{BASE_URL}/visualization/current"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as response:
        viz = json.loads(response.read().decode())
        print(f"✓ Visualization successful")
        print(f"  Total batches: {len(viz['batches'])}")
        print(f"  Total stations: {len(viz['stations'])}")
        for batch in viz['batches']:
            print(f"  - Batch {batch['batch_id']}: {batch['batch_name']} at {batch['leading_edge_km']:.2f} km")
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    print(f"Response: {e.read().decode()}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
