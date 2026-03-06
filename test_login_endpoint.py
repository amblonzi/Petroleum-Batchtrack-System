
import requests

def test_login_endpoint():
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "testuser",
        "password": "password123"
    }
    try:
        print(f"Sending POST request to {url}...")
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login_endpoint()
