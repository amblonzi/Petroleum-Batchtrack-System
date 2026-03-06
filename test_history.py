
import urllib.request
import json

def test_history():
    url = "http://localhost:8000/api/flow-entries/history?limit=5"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Count: {len(data)}")
            if len(data) > 0:
                print("First entry:", data[0])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_history()
