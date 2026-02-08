"""
Day 5: Token Bucket Rate Limiter

Implements the industry-standard Token Bucket Algorithm for API rate limiting.
Used by companies like AWS, Google, and Stripe to control request rates.

Usage:
    python 08_03_2026_token_bucket_rate_limiter.py
"""

import time
import threading
from typing import Optional


class RateLimiter:
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        :param max_tokens: Maximum capacity of the bucket.
        :param refill_rate: Number of tokens added per second.
        """
        self.max_tokens = float(max_tokens)
        self.refill_rate = refill_rate
        self.tokens = float(max_tokens)
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def _refill(self):
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * self.refill_rate
        if new_tokens > 0:
            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_update = now
        
    def allow_request(self, tokens_to_consume: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens_to_consume:
                self.tokens -= tokens_to_consume
                return True
            return False
        

    def wait_and_consume(self, tokens_to_consume: int = 1):
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= tokens_to_consume:
                    self.tokens -= tokens_to_consume
                    return 
                
                tokens_needed = tokens_to_consume - self.tokens
                wait_time = tokens_needed / self.refill_rate
            time.sleep(wait_time)


if __name__ == "__main__":
    limiter = RateLimiter(max_tokens=10, refill_rate=1)

    print("Bursting 6 requests...")
    
    for i in range(6):
        allowed = limiter.allow_request()
        if allowed:
            print(f"Request {i+1} allowed")
        else:
            print(f"Request {i+1} blocked")
            time.sleep(1)

    print("Waiting for 3 seconds...")
    time.sleep(3)
    
    print("Consuming 4 tokens...")
    limiter.wait_and_consume(4)
