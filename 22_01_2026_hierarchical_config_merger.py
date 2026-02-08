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
    if visited is None:
        visited = set()
    
    # Circular reference protection
    base_id = id(base)
    if base_id in visited:
        return copy.deepcopy(base)
    visited.add(base_id)
    
    result = copy.deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value, visited.copy())
        else:
            result[key] = copy.deepcopy(value)
    
    return result


def get_nested_value(config: Dict[str, Any], key_path: str) -> Any:
    """Get value from nested dictionary using dot notation."""
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    
    return value


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config."""
    result = copy.deepcopy(config)
    
    # Map environment variables to config paths
    env_mappings = {
        'APP_DATABASE_HOST': 'database.host',
        'APP_DATABASE_PORT': 'database.port',
        'APP_VERSION': 'version',
        'APP_NAME': 'app_name'
    }
    
    for env_var, config_path in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value:
            # Type conversion for known numeric fields
            if config_path.endswith('.port'):
                try:
                    env_value = int(env_value)
                except ValueError:
                    continue
            
            # Set nested value
            keys = config_path.split('.')
            current = result
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
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