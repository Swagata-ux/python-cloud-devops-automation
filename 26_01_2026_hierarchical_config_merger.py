"""
Day 4: Hierarchical Config Merger

Deep merges base configuration with overrides and validates required keys.
Supports nested dictionaries, environment variable overrides, and type validation.

🎯 Features:
- Deep merge without mutating original config
- Nested key validation (e.g., "database.port")
- Environment variable mapping
- Type validation
- Circular reference protection

Usage:
    python hierarchical_config_merger.py
"""

import copy
import os
import sys
from typing import Dict, List, Any, Set


class MissingConfigError(Exception):
    """Raised when required configuration keys are missing."""
    pass


def deep_merge(base: Dict[str, Any], override: Dict[str, Any], visited: Set[int] = None) -> Dict[str, Any]:
    """Deep merge two dictionaries without mutating the original."""
    # visited: Parameter name tracking processed objects
    # Set[int]: Type hint - set containing integers (object IDs)
    # = None: Default value making parameter optional for first call
    # Why: Prevents infinite recursion in circular references
    
    if visited is None:  # First call initialization
        visited = set()  # Create empty set to track object IDs
    
    # Circular reference protection - prevents infinite loops
    base_id = id(base)  # Get unique integer ID of base dictionary object
    if base_id in visited:  # Already processed this exact object?
        return copy.deepcopy(base)  # Return safe copy, stop recursion
    visited.add(base_id)  # Mark this object ID as "seen"
    
    # result: Variable name for our working copy
    # =: Assignment operator
    # copy.deepcopy(base): Creates completely independent copy of base
    # Why deepcopy: Recursively copies all nested objects, prevents mutation
    result = copy.deepcopy(base)
    
    # Iterate through each key-value pair in override dictionary
    for key, value in override.items():
        # Check if we need to merge dictionaries recursively:
        # 1. key exists in result (base had this key)
        # 2. result[key] is dict (base value is dictionary)
        # 3. value is dict (override value is also dictionary)
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursive merge: merge nested dictionaries
            # visited.copy(): Pass copy of visited set to avoid cross-contamination
            result[key] = deep_merge(result[key], value, visited.copy())
        else:
            # Simple override: replace base value with override value
            # copy.deepcopy(value): Ensure we don't share references
            result[key] = copy.deepcopy(value)
    
    return result


def get_nested_value(config: Dict[str, Any], key_path: str) -> Any:
    """Get value from nested dictionary using dot notation."""
    # Split dot-separated path into individual keys
    # Example: "database.port" becomes ["database", "port"]
    keys = key_path.split('.')
    value = config  # Start traversal from root config
    
    # Navigate through each key in the path
    for key in keys:
        # Safety checks before accessing nested key:
        # 1. Current value must be a dictionary
        # 2. Key must exist in current dictionary
        if not isinstance(value, dict) or key not in value:
            return None  # Path doesn't exist, return None
        value = value[key]  # Move deeper into nested structure
    
    return value  # Return the final nested value


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config."""
    # Create independent copy to avoid mutating input
    result = copy.deepcopy(config)
    
    # Dictionary mapping environment variable names to config paths
    # Key: Environment variable name (what to look for in os.environ)
    # Value: Dot-notation path in config (where to set the value)
    env_mappings = {
        'APP_DATABASE_HOST': 'database.host',  # Maps APP_DATABASE_HOST -> config['database']['host']
        'APP_DATABASE_PORT': 'database.port',  # Maps APP_DATABASE_PORT -> config['database']['port']
        'APP_VERSION': 'version',              # Maps APP_VERSION -> config['version']
        'APP_NAME': 'app_name'                 # Maps APP_NAME -> config['app_name']
    }
    
    # Process each environment variable mapping
    for env_var, config_path in env_mappings.items():
        # Get environment variable value (returns None if not set)
        env_value = os.getenv(env_var)
        if env_value:  # Only process if environment variable exists
            # Smart type conversion for known numeric fields
            if config_path.endswith('.port'):  # Port numbers should be integers
                try:
                    env_value = int(env_value)  # Convert string to integer
                except ValueError:
                    continue  # Skip invalid port values
            
            # Navigate to nested location and set value
            keys = config_path.split('.')  # Split path into individual keys
            current = result  # Start from root of config
            # Navigate to parent of target key (all keys except last)
            for key in keys[:-1]:
                if key not in current:  # Create missing intermediate dictionaries
                    current[key] = {}
                current = current[key]  # Move deeper
            # Set the final value using the last key in path
            current[keys[-1]] = env_value
    
    return result


def validate_types(base: Dict[str, Any], merged: Dict[str, Any], path: str = "") -> None:
    """Validate that override types match base types."""
    for key, base_value in base.items():
        current_path = f"{path}.{key}" if path else key
        
        if key in merged:
            merged_value = merged[key]
            
            if isinstance(base_value, dict) and isinstance(merged_value, dict):
                validate_types(base_value, merged_value, current_path)
            elif type(base_value) != type(merged_value):
                print(f"⚠️  Type mismatch at {current_path}: expected {type(base_value).__name__}, got {type(merged_value).__name__}")


def validate_required_keys(config: Dict[str, Any], required_keys: List[str]) -> None:
    """Validate that all required keys exist and are not None."""
    missing_keys = []
    
    for key_path in required_keys:
        value = get_nested_value(config, key_path)
        if value is None:
            missing_keys.append(key_path)
    
    if missing_keys:
        raise MissingConfigError(f"Missing required keys: {', '.join(missing_keys)}")


def main():
    """Main function demonstrating the hierarchical config merger."""
    
    # Base configuration
    base_config = {
        "app_name": "CloudPortal",
        "version": "1.0.0",
        "database": {
            "host": "localhost",
            "port": 5432,
            "settings": {"max_connections": 100}
        },
        "features": ["logging", "monitoring"]
    }
    
    # Override configuration
    overrides = {
        "version": "1.1.0",
        "database": {
            "host": "prod-db-01.internal",
            "settings": {"max_connections": 500}
        },
        "features": ["logging", "monitoring", "caching"]
    }
    
    # Required keys to validate
    required_keys = ["app_name", "database.host", "database.port"]
    
    try:
        print("🔧 Starting hierarchical config merge...")
        
        # Step 1: Deep merge
        merged_config = deep_merge(base_config, overrides)
        
        # Step 2: Apply environment variable overrides
        merged_config = apply_env_overrides(merged_config)
        
        # Step 3: Type validation
        validate_types(base_config, merged_config)
        
        # Step 4: Validate required keys
        validate_required_keys(merged_config, required_keys)
        
        print("✅ Configuration merge completed successfully!")
        print("\n📋 Merged Configuration:")
        print(f"  app_name: {merged_config['app_name']}")
        print(f"  version: {merged_config['version']}")
        print(f"  database.host: {merged_config['database']['host']}")
        print(f"  database.port: {merged_config['database']['port']}")
        print(f"  database.settings.max_connections: {merged_config['database']['settings']['max_connections']}")
        print(f"  features: {merged_config['features']}")
        
        # Verify original config wasn't mutated
        assert base_config['version'] == "1.0.0", "Original config was mutated!"
        print("\n✅ Original configuration preserved (no mutation)")
        
        return merged_config
        
    except MissingConfigError as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()