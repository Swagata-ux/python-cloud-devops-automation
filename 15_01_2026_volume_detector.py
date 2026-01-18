"""
Cloud Volume Detector - Improved Version
Detects orphaned and zombie volumes to calculate cost savings.

Orphaned: volumes with attachment_id = None
Zombie: volumes attached to non-existent instances
"""
from typing import List, Dict, Union
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def detect_orphaned_volumes(
    instances: List[Dict[str, str]], 
    volumes: List[Dict[str, Union[str, int, float, None]]], 
    dry_run: bool = False
) -> Dict[str, Union[List[str], float]]:
    """
    Detect orphaned and zombie volumes with O(N+M) complexity.
    
    Args:
        instances: List of active VM instances
        volumes: List of storage volumes
        dry_run: If True, log preview of deletions
        
    Returns:
        Dict with orphaned_ids, zombie_ids, and total_savings
    """
    if not instances or not volumes:
        logging.warning("Empty instances or volumes list provided")
        return {'orphaned_ids': [], 'zombie_ids': [], 'total_savings': 0.0}
    
    # Create set for O(1) lookup
    active_instance_ids = {instance['id'] for instance in instances}
    
    orphaned_ids = []
    zombie_ids = []
    total_savings = 0.0
    
    for volume in volumes:
        try:
            vol_id = volume['id']
            attachment_id = volume['attachment_id']
            size_gb = volume['size_gb']
            cost_per_gb = volume['cost_per_gb']
            
            monthly_cost = size_gb * cost_per_gb
            
            if attachment_id is None:
                # Orphaned volume
                orphaned_ids.append(vol_id)
                total_savings += monthly_cost
                
                if dry_run:
                    logging.info(f"[DRY RUN] Would delete orphaned volume {vol_id} (${monthly_cost:.2f}/month)")
                    
            elif attachment_id not in active_instance_ids:
                # Zombie volume
                zombie_ids.append(vol_id)
                total_savings += monthly_cost
                
                logging.warning(f"Zombie volume detected: {vol_id} -> {attachment_id}")
                
                if dry_run:
                    logging.info(f"[DRY RUN] Would delete zombie volume {vol_id} (${monthly_cost:.2f}/month)")
                    
        except KeyError as e:
            logging.error(f"Missing required field in volume {volume.get('id', 'unknown')}: {e}")
        except (TypeError, ValueError) as e:
            logging.error(f"Invalid data in volume {volume.get('id', 'unknown')}: {e}")
    
    return {
        'orphaned_ids': orphaned_ids,
        'zombie_ids': zombie_ids,
        'total_savings': round(total_savings, 2)
    }

def generate_report(result: Dict[str, Union[List[str], float]]) -> None:
    """Generate a formatted report of the analysis"""
    print("\nCloud Volume Analysis Report")
    print("=" * 40)
    
    orphaned = result['orphaned_ids']
    zombie = result['zombie_ids']
    savings = result['total_savings']
    
    print(f"Orphaned Volumes: {len(orphaned)}")
    for vol_id in orphaned:
        print(f"  • {vol_id}")
    
    print(f"\nZombie Volumes: {len(zombie)}")
    for vol_id in zombie:
        print(f"  • {vol_id}")
    
    print(f"\nTotal Monthly Savings: ${savings:.2f}")
    print(f"Annual Savings: ${savings * 12:.2f}")

def main():
    """Main function with sample data and testing"""
    # Sample data
    instances = [
        {"id": "i-123", "name": "production-db"},
        {"id": "i-456", "name": "web-server-1"}
    ]
    
    volumes = [
        {"id": "vol-001", "attachment_id": "i-123", "size_gb": 100, "cost_per_gb": 0.10},
        {"id": "vol-002", "attachment_id": None, "size_gb": 50, "cost_per_gb": 0.10},
        {"id": "vol-003", "attachment_id": "i-789", "size_gb": 20, "cost_per_gb": 0.05},
        {"id": "vol-004", "attachment_id": None, "size_gb": 30, "cost_per_gb": 0.08},
    ]
    
    print("Testing Volume Detection...")
    
    # Normal analysis
    result = detect_orphaned_volumes(instances, volumes)
    generate_report(result)
    
    # Dry run analysis
    print("\n" + "=" * 40)
    print("DRY RUN MODE")
    print("=" * 40)
    detect_orphaned_volumes(instances, volumes, dry_run=True)

if __name__ == "__main__":
    main()