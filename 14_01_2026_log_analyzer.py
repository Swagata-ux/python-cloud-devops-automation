"""
Web Server Log Analyzer - Improved Version
Analyzes web server logs to find top 3 IPs and error rate.

Log format: [TIMESTAMP] IP_ADDRESS "METHOD PATH PROTOCOL" STATUS_CODE RESPONSE_SIZE
Example: [2023-10-01 10:00:01] 192.168.1.1 "GET /index.html HTTP/1.1" 200 512
"""
import re
from collections import Counter
from typing import Union, Dict, List, Tuple, Optional

def parse_log_line(line: str) -> Optional[Tuple[str, int]]:
    """Parse a single log line and extract IP address and status code"""
    pattern = r'\[.*?\]\s+(\S+)\s+".*?"\s+(\d+)\s+\d+'
    match = re.match(pattern, line.strip())
    
    if match:
        ip_address = match.group(1)
        status_code = int(match.group(2))
        return ip_address, status_code
    
    return None

def analyze_logs(log_input: Union[List[str], str]) -> Dict[str, Union[List[Tuple[str, int]], float]]:
    """
    Analyze web server logs to find top IPs and error rate.
    
    Args:
        log_input: Either a list of log lines or a file path
        
    Returns:
        Dictionary with 'top_ips' and 'error_rate'
    """
    # Handle file input vs list input
    if isinstance(log_input, str):
        try:
            with open(log_input, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{log_input}' not found")
            return {'top_ips': [], 'error_rate': 0.0}
    else:
        lines = log_input
    
    ip_counter = Counter()
    total_requests = 0
    error_count = 0
    malformed_count = 0
    
    for line_num, line in enumerate(lines, 1):
        parsed = parse_log_line(line)
        
        if parsed:
            ip_address, status_code = parsed
            ip_counter[ip_address] += 1
            total_requests += 1
            
            if status_code >= 400:
                error_count += 1
        else:
            malformed_count += 1
    
    # Calculate error rate (avoid division by zero)
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
    
    # Print summary
    print(f"Processed {len(lines)} lines:")
    print(f"  Valid requests: {total_requests}")
    print(f"  Malformed lines: {malformed_count}")
    print(f"  Error requests: {error_count}")
    
    return {
        'top_ips': ip_counter.most_common(3),
        'error_rate': error_rate
    }

def main():
    """Main function with sample data"""
    sample_logs = [
        '[2023-10-01 10:00:01] 192.168.1.1 "GET /index.html HTTP/1.1" 200 512',
        '[2023-10-01 10:00:02] 192.168.1.2 "GET /about.html HTTP/1.1" 404 128',
        '[2023-10-01 10:00:03] 192.168.1.1 "POST /api/data HTTP/1.1" 500 256',
        '[2023-10-01 10:00:04] 192.168.1.3 "GET /contact.html HTTP/1.1" 200 1024',
        '[2023-10-01 10:00:05] 192.168.1.1 "GET /home.html HTTP/1.1" 200 768',
        '[2023-10-01 10:00:06] 192.168.1.2 "GET /services.html HTTP/1.1" 403 64',
        'malformed line',
    ]
    
    print("Web Server Log Analysis")
    print("=" * 40)
    
    result = analyze_logs(sample_logs)
    
    print("\nResults:")
    print("-" * 40)
    print("Top 3 IP Addresses:")
    for i, (ip, count) in enumerate(result['top_ips'], 1):
        print(f"  {i}. {ip:<15} ({count} requests)")
    
    print(f"\nError Rate: {result['error_rate']:.2f}%")

if __name__ == "__main__":
    main()