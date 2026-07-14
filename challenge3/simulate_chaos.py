import sys
import requests

BACKEND_URL = "http://localhost:8000"

def run_chaos_test():
    print("[!] Starting Challenge 3 Chaos Test...")
    print("[*] Sending malformed payload missing the required 'name' property...")

    malformed_payload = {
        "itme_name": "Organic Milk",  # Intentional typo in key
        "quantity": "three bags",     # Supposed to be an integer
    }

    try:
        response = requests.post(f"{BACKEND_URL}/items", json=malformed_payload, timeout=5)
        if response.status_code == 500:
            print("[-] CRITICAL FAILURE: The server threw a 500 Internal Server Error or crashed completely.")
        else:
            print(f"[-] Server responded with code {response.status_code}. Response text: {response.text}")
    except requests.exceptions.RequestException as e:
        print("[X] SUCCESSFUL CHAOS: The backend server crashed completely and closed the connection!")
        sys.exit(0)

if __name__ == "__main__":
    run_chaos_test()
