"""
Service Health Checker - Improved Version
Monitors microservice health with exponential backoff retry logic.

Retry delays: 1s, 2s, 4s (exponential backoff)
Max retries: 3 attempts before marking service as DOWN
"""
import time
import random
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
MAX_RETRIES = 3
BASE_DELAY = 1  # Base delay in seconds

def call_api(url: str) -> int:
    """Mock API call that simulates real-world network behavior"""
    outcomes = ['success', 'server_error', 'connection_error']
    weights = [0.6, 0.3, 0.1]  # 60% success, 30% server error, 10% connection error
    
    outcome = random.choices(outcomes, weights=weights)[0]
    
    if outcome == 'success':
        return 200
    elif outcome == 'server_error':
        return random.choice([500, 502, 503, 504])
    else:
        raise ConnectionError(f"Failed to connect to {url}")

def check_service_health(service_name: str, url: str) -> Dict[str, Any]:
    """
    Check service health with exponential backoff retry logic.
    
    Args:
        service_name: Name of the service
        url: Health check endpoint URL
        
    Returns:
        Dict with status ('UP'/'DOWN'), attempts count, and response time
    """
    attempts = 0
    start_time = time.time()
    
    while attempts <= MAX_RETRIES:
        attempts += 1
        attempt_start = time.time()
        
        try:
            status_code = call_api(url)
            response_time = (time.time() - attempt_start) * 1000  # Convert to ms
            
            if status_code == 200:
                total_time = (time.time() - start_time) * 1000
                logging.info(f"✅ {service_name} is UP (attempt {attempts}, {response_time:.0f}ms)")
                return {
                    "status": "UP",
                    "attempts": attempts,
                    "response_time_ms": round(response_time, 2),
                    "total_time_ms": round(total_time, 2)
                }
            else:
                logging.warning(f"❌ {service_name} returned HTTP {status_code}")
                
        except ConnectionError as e:
            logging.warning(f"❌ {service_name} connection failed: {str(e)}")
        
        # Calculate delay for next retry (exponential backoff)
        if attempts <= MAX_RETRIES:
            delay = BASE_DELAY * (2 ** (attempts - 1))
            logging.info(f"⏳ Retrying {service_name} in {delay}s... (attempt {attempts}/{MAX_RETRIES + 1})")
            time.sleep(delay)
    
    total_time = (time.time() - start_time) * 1000
    logging.error(f"❌ {service_name} is DOWN after {attempts} attempts")
    
    return {
        "status": "DOWN",
        "attempts": attempts,
        "response_time_ms": None,
        "total_time_ms": round(total_time, 2)
    }

def check_all_services(services: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """Check health of all services"""
    if not services:
        logging.warning("No services provided to check")
        return {}
    
    results = {}
    total_start = time.time()
    
    logging.info(f"Starting health check for {len(services)} services...")
    
    for service_name, url in services.items():
        logging.info(f"\n{'='*60}")
        logging.info(f"Checking {service_name}")
        logging.info('='*60)
        
        try:
            results[service_name] = check_service_health(service_name, url)
        except Exception as e:
            logging.error(f"Unexpected error checking {service_name}: {e}")
            results[service_name] = {
                "status": "ERROR",
                "attempts": 0,
                "response_time_ms": None,
                "total_time_ms": None,
                "error": str(e)
            }
    
    total_time = (time.time() - total_start) * 1000
    logging.info(f"\nHealth check completed in {total_time:.0f}ms")
    
    return results

def generate_report(results: Dict[str, Dict[str, Any]]) -> None:
    """Generate a formatted health check report"""
    if not results:
        print("No results to report")
        return
    
    print("\n" + "="*70)
    print("SERVICE HEALTH REPORT")
    print("="*70)
    
    up_count = sum(1 for r in results.values() if r['status'] == 'UP')
    down_count = len(results) - up_count
    
    print(f"Services UP: {up_count} | Services DOWN: {down_count}")
    print("-"*70)
    
    for service, status in results.items():
        emoji = "✅" if status['status'] == 'UP' else "❌"
        attempts = status['attempts']
        response_time = status.get('response_time_ms', 'N/A')
        
        if response_time != 'N/A':
            print(f"{emoji} {service:<20} {status['status']:<4} ({attempts} attempts, {response_time}ms)")
        else:
            print(f"{emoji} {service:<20} {status['status']:<4} ({attempts} attempts)")

def main():
    """Main function"""
    services = {
        "auth-service": "https://auth.example.com/health",
        "payment-gateway": "https://payments.example.com/health",
        "inventory-api": "https://inventory.example.com/health",
        "user-service": "https://users.example.com/health"
    }
    
    # Run health checks
    results = check_all_services(services)
    
    # Generate report
    generate_report(results)

if __name__ == "__main__":
    main()