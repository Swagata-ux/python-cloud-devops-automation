"""
Day 7: Thread-Safe Secret Cache with TTL

Implements a thread-safe caching layer for secrets with time-to-live expiration.
Prevents cache stampede and reduces expensive vault API calls.

Usage:
    python 21_02_2026_thread_safe_secret_cache.py
"""

import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(threadName)s: %(message)s')

def fetch_secret_from_vault(key: str) -> str:
    """Simulates a slow network call to a Secret Vault (e.g., AWS Secrets Manager)."""
    logging.info(f"--- Calling Vault API for '{key}' (Slow) ---")
    time.sleep(2) # Simulate 2-second network latency
    return f"super-secret-value-for-{key}"

class SecretCache:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self.cache = {} # Format: { key: {"value": str, "expiry": float} }
        self.lock = threading.Lock()
    def get_secret(self, key: str) -> str:
        now = time.time()
        # 1. First Check (Fast Path): No locking.
        # If the secret is in cache and hasn't expired, return it immediately.
        if key in self.cache and now < self.cache[key]["expiry"]:
            logging.info(f"Cache Hit for  {key}")
            return self.cache[key]["value"]
        # 2. Acquire Lock: If we reach here, we likely need to update the cache.
        with self.lock:
        # 3. Double-Check (Safety Path): 
        # While this thread was waiting for the lock, another thread 
        # might have already fetched the secret and updated the cache.
            now = time.time()
            if key in self.cache and now < self.cache[key]["expiry"]:
                logging.info(f"Cache Hit for '{key}' (after waiting for lock)")
                return self.cache[key]["value"]
            # 4. Cache Miss / Expired: Perform the expensive operation
            logging.info(f"Cache Miss/Expired for '{key}'. Fetching fresh value...")
            secret_value = fetch_secret_from_vault(key)
            # Store with new expiry
            self.cache[key] = {
                "value" : secret_value,
                "expiry" : now + self.ttl
            }

            return secret_value



if __name__ == "__main__":
    # Initialize cache with a 5-second TTL
    vault_cache = SecretCache(ttl_seconds=5)

    def worker_task(secret_name):
        val = vault_cache.get_secret(secret_name)
        # logging.info(f"Result: {val}")

    # Simulate a "Cache Stampede": 5 threads all asking for the same secret at once
    threads = []
    logging.info("Starting 5 threads simultaneously...")

    for i in range(5):
        t = threading.Thread(target=worker_task, args=("api-key-prod"), name=f"Thread-{i+1}")
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    print("\n--- Waiting 6 seconds for TTL to expire ---")

    time.sleep(6)

    logging.info("Requesting after expiration...")
    vault_cache.get_secret("api-key-prod")







        