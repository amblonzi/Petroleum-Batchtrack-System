import json
import http.client
import sys
import urllib.parse

BASE_HOST = "localhost"
BASE_PORT = 8000

def make_request(method, path, body=None, headers=None):
    if headers is None:
        headers = {}
    if body:
        headers["Content-Type"] = "application/json"
        body_json = json.dumps(body)
    else:
        body_json = None
        
    conn = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
    try:
        conn.request(method, path, body_json, headers)
        response = conn.getresponse()
        data = response.read().decode()
        return response.status, data
    except Exception as e:
        print(f"Request failed: {e}")
        return None, None
    finally:
        conn.close()

def make_form_request(method, path, body=None):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body_encoded = urllib.parse.urlencode(body) if body else None
    
    conn = http.client.HTTPConnection(BASE_HOST, BASE_PORT)
    try:
        conn.request(method, path, body_encoded, headers)
        response = conn.getresponse()
        data = response.read().decode()
        return response.status, data
    except Exception as e:
        print(f"Request failed: {e}")
        return None, None
    finally:
        conn.close()

def test_admin_flow():
    # 1. Register a new user
    username = "admin_test_v2"
    password = "password123"
    print(f"1. Registering user '{username}'...")
    
    status, data = make_request("POST", "/api/auth/register", {
        "username": username,
        "password": password,
        "full_name": "Admin Test User V2"
    })
    
    if status == 200:
        print("   Success: User registered.")
    elif status == 400 and "already registered" in data:
        print("   User already exists, continuing...")
    else:
        print(f"   Failed to register: {status} {data}")
        sys.exit(1)

    # 2. Login to get token (Login expects Form Data, not JSON)
    print("2. Logging in...")
    status, data = make_form_request("POST", "/api/auth/login", {
        "username": username,
        "password": password
    })
    
    if status != 200:
        print(f"   Login failed: {status} {data}")
        sys.exit(1)
    
    try:
        token = json.loads(data)["access_token"]
        print("   Success: Got token.")
    except Exception as e:
        print(f"   Failed to parse token: {e}")
        sys.exit(1)

    # 3. Clear data
    print("3. Clearing operational data...")
    headers = {"Authorization": f"Bearer {token}"}
    status, data = make_request("DELETE", "/api/admin/clear-data", headers=headers)
    
    if status == 200:
        print(f"   Success: {data}")
    else:
        print(f"   Failed to clear data: {status} {data}")

if __name__ == "__main__":
    test_admin_flow()
