import concurrent.futures
import requests

BACKEND_URL = "http://localhost:8000"

def simulate_concurrent_edit(user_id, item_id, target_quantity):
    payload = {"quantity": target_quantity}
    print(f"[*] User #{user_id} is simultaneously updating item {item_id} quantity to {target_quantity}...")
    response = requests.patch(f"{BACKEND_URL}/items/{item_id}", json=payload)
    return response.status_code

def run_concurrency_chaos():
    print("[!] Starting Challenge 4 Concurrency Overwrite Test...")
    item_id = 1 # Target baseline item
    total_requests = 10

    with concurrent.futures.ThreadPoolExecutor(max_workers=total_requests) as executor:
        futures = [executor.submit(simulate_concurrent_edit, i+1, item_id, i+2) for i in range(total_requests)]
        status_codes = [f.result() for f in concurrent.futures.as_completed(futures)]

    print("\n--- Chaos Results ---")
    print(f"[!] Server HTTP Response Codes received: {status_codes}")

    final_state = requests.get(f"{BACKEND_URL}/items/{item_id}").json()
    print(f"[*] Final item state in database: {final_state}")

    if 409 in status_codes:
        print("[+] SUCCESS: The system successfully intercepted concurrent modifications and threw a 409 Conflict!")
    elif final_state.get("quantity") != (total_requests + 1):
        print("[-] CRITICAL FAILURE: Lost Update Problem confirmed! Data corruption occurred.")
    else:
        print("[+] SUCCESS: State remained consistent.")

if __name__ == "__main__":
    run_concurrency_chaos()
