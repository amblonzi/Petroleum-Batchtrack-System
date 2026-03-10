import json
import http.client
import sys
import urllib.parse

BASE_HOST = "localhost"
BASE_PORT = 8001 # Backend is on 8001 via docker-compose

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

def verify_admin_user_creation():
    # 1. Login as existing admin (using known credentials from previous logs or seeding)
    # Default admin is often admin/admin in these setups
    print("1. Logging in as admin...")
    status, data = make_form_request("POST", "/auth/login", {
        "username": "admin",
        "password": "admin"
    })
    
    if status != 200:
        print(f"   Login failed: {status} {data}")
        sys.exit(1)
    
    token = json.loads(data)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test the new POST /admin/users endpoint
    new_user = {
        "username": "tester_admin_api",
        "password": "password123",
        "full_name": "API Test User",
        "is_admin": False
    }
    print(f"2. Creating new user '{new_user['username']}' via Admin API...")
    status, data = make_request("POST", "/admin/users", new_user, headers=headers)
    
    if status == 200:
        print("   Success: User created via Admin API.")
    elif status == 400 and "already registered" in data:
        print("   User already exists, test partial success (endpoint reached).")
    else:
        print(f"   Failed to create user: {status} {data}")
        sys.exit(1)

    # 3. Verify user appears in the list
    print("3. Fetching user list...")
    status, data = make_request("GET", "/admin/users", headers=headers)
    if status == 200:
        users = json.loads(data)
        if any(u['username'] == new_user['username'] for u in users):
            print("   Success: New user found in admin user list.")
        else:
            print("   Failure: New user NOT found in admin user list.")
    else:
        print(f"   Failed to fetch user list: {status} {data}")

if __name__ == "__main__":
    verify_admin_user_creation()
