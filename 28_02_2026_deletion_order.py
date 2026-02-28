"""
Day 8: The Cloud Resource Deletion Resolver

1. Problem Statement
You are given a dictionary representing cloud resources and their dependencies. A dependency means "Resource A depends on Resource B" (so Resource B must exist for Resource A to function).
Your task is to write a script that calculates a safe deletion order.
Rule: If Resource A depends on Resource B, Resource A must be deleted before Resource B.
Edge Case: If there is a circular dependency (A depends on B, and B depends on A), deletion is impossible. Your script must detect this and raise an error.

2. Input/Output Expectations
Input: A dictionary where the key is the resource name and the value is a list of resources it depends on.

Python
dependencies = {
    "db-instance": ["security-group", "subnet-a"],
    "web-server": ["security-group", "subnet-a"],
    "security-group": ["vpc-prod"],
    "subnet-a": ["vpc-prod"],
    "vpc-prod": []
}

Output: A list of strings showing the order in which to delete resources.
Possible valid output:
['db-instance', 'web-server', 'security-group', 'subnet-a', 'vpc-prod']
(Note: 'web-server' could come before 'db-instance', but both must come before 'security-group'.)


3. Constraints & Assumptions
Algorithm: This is a Topological Sort problem. For deletion, you are essentially looking for the reverse of the creation order.
Cycles: If the input is {"A": ["B"], "B": ["A"]}, the script should raise a CircularDependencyError.
Scale: Assume there could be hundreds of resources.
Type Hinting: Use Python’s typing module for clear signatures.


4. Bonus / Follow-up Challenges
Parallel Execution Groups: Instead of a simple list, return a list of lists representing "batches" of resources that can be deleted simultaneously.
Example: [['db-instance', 'web-server'], ['security-group', 'subnet-a'], ['vpc-prod']]
Validation: Ensure that if a resource mentions a dependency (e.g., "vpc-prod"), that dependency also exists as a key in the dictionary.
Visualizing the Graph: (Theoretical) How would you represent this graph in memory? (Hint: Adjacency List).
"""

from collections import deque
from typing import List, Dict, Set

class CircularDependencyError(Exception):
    """Raised when resources have a circular dependency, making deletion impossible."""
    pass

def get_deletion_order(dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """
    Calculates a safe deletion order using Kahn's Algorithm.
    Returns a list of batches, where each batch contains resources 
    that can be deleted in parallel.
    """
    # 1. Build the Graph and Track In-Degrees
    # in_degree[u] will store how many resources depend on 'u'
    in_degree = {resource: 0 for resource in dependencies}
    # adjacency_list[u] will store which resources 'u' depends on
    # (i.e., who is freed up when 'u' is deleted)
    adj = {resource: [] for resource in dependencies}

    for resource, deps in dependencies.items():
        for dep in deps:
            if dep not in dependencies:
                # Industry standard: validation for missing resources
                raise ValueError(f"Resource '{resource}' depends on unknown resource '{dep}'")
            
            # If A depends on B, B has one more 'dependent'.
            # When A is deleted, B is one step closer to being deletable.
            adj[resource].append(dep)
            in_degree[dep] += 1

    # 2. Find initial resources safe to delete (those with 0 dependents)
    queue = deque([r for r, count in in_degree.items() if count == 0])
    
    deletion_batches = []
    processed_count = 0

    # 3. Process the queue in batches (for parallel execution)
    while queue:
        batch_size = len(queue)
        current_batch = []

        for _ in range(batch_size):
            u = queue.popleft()
            current_batch.append(u)
            processed_count += 1

            # For every resource 'v' that 'u' depended on...
            for v in adj[u]:
                in_degree[v] -= 1
                # If no more resources depend on 'v', it's safe to delete
                if in_degree[v] == 0:
                    queue.append(v)
        
        deletion_batches.append(current_batch)

    # 4. Cycle Detection
    if processed_count != len(dependencies):
        raise CircularDependencyError("Circular dependency detected! Deletion impossible.")

    return deletion_batches

# --- Testing the implementation ---
if __name__ == "__main__":
    cloud_resources = {
        "db-instance": ["security-group", "subnet-a"],
        "web-server": ["security-group", "subnet-a"],
        "security-group": ["vpc-prod"],
        "subnet-a": ["vpc-prod"],
        "vpc-prod": []
    }

    try:
        batches = get_deletion_order(cloud_resources)
        print("Safe Deletion Order (By Batches):")
        for i, batch in enumerate(batches):
            print(f"Step {i+1}: Delete {batch}")
            
        # Flattened list for a simple sequence
        flattened = [item for sublist in batches for item in sublist]
        print(f"\nSequential order: {' -> '.join(flattened)}")

    except (CircularDependencyError, ValueError) as e:
        print(f"Error: {e}")