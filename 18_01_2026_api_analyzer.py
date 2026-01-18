"""
API Performance Analyzer - Improved Version
Finds the top 10 slowest API endpoints from log files.

Supports multiple log formats:
- Custom: 2026-01-15T10:22:11Z GET /api/users 200 1234ms
- Apache: "GET /api/users HTTP/1.1" 200 1234 0.523
"""
import re
from collections import defaultdict
from typing import List, Tuple, Optional

def parse_log_line(line: str) -> Optional[Tuple[str, float]]:
    """Parse log line to extract endpoint and response time in ms"""
    patterns = [
        # Custom format: GET /api/users 200 1234ms
        r'\s(GET|POST|PUT|DELETE)\s+(\S+).*?(\d+)ms',
        # Apache format: "GET /api/users HTTP/1.1" 200 1234 0.523
        r'"(GET|POST|PUT|DELETE)\s+(\S+)[^"]*"\s+\d+\s+\d+\s+([\d.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            method, path = match.group(1), match.group(2)
            endpoint = f"{method} {path}"
            
            # Convert response time to milliseconds
            time_str = match.group(3)
            if '.' in time_str:  # Apache format (seconds)
                response_time = float(time_str) * 1000
            else:  # Custom format (milliseconds)
                response_time = float(time_str)
            
            return endpoint, response_time
    
    return None

def analyze_api_performance(log_file: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """Analyze log file and return top N slowest endpoints"""
    stats = defaultdict(lambda: {"total_time": 0.0, "count": 0})
    
    try:
        with open(log_file, "r") as f:
            for line_num, line in enumerate(f, 1):
                parsed = parse_log_line(line.strip())
                if parsed:
                    endpoint, response_time = parsed
                    stats[endpoint]["total_time"] += response_time
                    stats[endpoint]["count"] += 1
    
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found")
        return []
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []
    
    if not stats:
        print("No valid log entries found")
        return []
    
    # Calculate averages and sort by response time
    averages = [
        (endpoint, data["total_time"] / data["count"])
        for endpoint, data in stats.items()
    ]
    
    return sorted(averages, key=lambda x: x[1], reverse=True)[:top_n]

def main():
    """Main function"""
    log_file = "sample_api.log"
    
    print(f"Analyzing API performance from: {log_file}")
    print("=" * 50)
    
    top_endpoints = analyze_api_performance(log_file)
    
    if top_endpoints:
        print("Top 10 Slowest Endpoints (by avg response time):")
        print("-" * 50)
        for i, (endpoint, avg_time) in enumerate(top_endpoints, 1):
            print(f"{i:2}. {endpoint:<30} {avg_time:8.2f}ms")
    else:
        print("No endpoints found to analyze")

if __name__ == "__main__":
    main()