"""
Configuration loader for the Surtax Oversight Pro application.
Loads default config and merges with county-specific settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def get_config_path() -> Path:
    """Get the path to the config directory."""
    if 'SURTAX_CONFIG_PATH' in os.environ:
        return Path(os.environ['SURTAX_CONFIG_PATH'])
    return Path(__file__).parent.parent / 'config'


def load_yaml(filepath: Path) -> Dict[str, Any]:
    """Load a YAML file and return as dictionary."""
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def resolve_env_vars(config: Dict) -> Dict:
    """Resolve ${VAR_NAME} environment variable placeholders in config."""
    import re

    def resolve_value(value):
        if isinstance(value, str):
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            for match in matches:
                env_value = os.environ.get(match, '')
                value = value.replace(f'${{{match}}}', env_value)
            return value
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item) for item in value]
        return value

    return resolve_value(config)


def load_config(county: str = 'marion') -> Dict[str, Any]:
    """Load configuration for a specific county."""
    config_path = get_config_path()
    default_config = load_yaml(config_path / 'default.yaml')
    county_config = load_yaml(config_path / 'counties' / f'{county.lower()}.yaml')
    merged = deep_merge(default_config, county_config)
    resolved = resolve_env_vars(merged)
    return resolved


def get_database_path(config: Dict) -> Path:
    """Get the database path from config."""
    db_config = config.get('database', {})
    db_path = db_config.get('path', 'data/surtax_pro.db')
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent
        return project_root / db_path
    return Path(db_path)
