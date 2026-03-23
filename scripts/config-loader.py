#!/usr/bin/env python3
"""TOML Configuration Loader for GDP MCP Server.

Loads configuration from a TOML file and exports values as environment variables.
This allows non-sensitive settings to be stored in config.toml while keeping
credentials in environment variables or .env files.

Usage:
    python config-loader.py /path/to/config.toml
"""
# This file includes AI-generated code - Review and modify as needed

import os
import sys
from pathlib import Path


def load_toml_config(config_path: str) -> dict:
    """Load configuration from TOML file.
    
    Uses tomllib (Python 3.11+) or falls back to toml package.
    """
    try:
        # Python 3.11+ has built-in tomllib
        import tomllib
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        # Fallback to toml package for older Python versions
        try:
            import toml
            with open(config_path, "r") as f:
                return toml.load(f)
        except ImportError:
            print("ERROR: Neither tomllib nor toml package available", file=sys.stderr)
            print("Install toml: pip install toml", file=sys.stderr)
            sys.exit(1)


def export_to_env(config: dict, prefix: str = "") -> None:
    """Recursively export configuration values to environment variables.
    
    Only exports values if the environment variable is not already set.
    This allows environment variables to override TOML config.
    
    Args:
        config: Configuration dictionary
        prefix: Prefix for environment variable names
    """
    for key, value in config.items():
        env_key = f"{prefix}{key}".upper()
        
        if isinstance(value, dict):
            # Recursively handle nested sections
            export_to_env(value, f"{env_key}_")
        else:
            # Only set if not already in environment
            if env_key not in os.environ:
                os.environ[env_key] = str(value)
                print(f"  {env_key}={value}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: config-loader.py <config.toml>", file=sys.stderr)
        sys.exit(1)
    
    config_path = Path(sys.argv[1])
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        config = load_toml_config(str(config_path))
        print(f"Configuration loaded from {config_path}")
        export_to_env(config)
        print("Configuration exported to environment variables")
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
