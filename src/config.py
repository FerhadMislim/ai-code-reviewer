"""
Configuration management and token storage
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    """Manage configuration and API tokens"""
    
    CONFIG_FILE = '.code_reviewer_config'
    
    @staticmethod
    def get_config_path() -> Path:
        """Get the configuration file path"""
        return Path.home() / ConfigManager.CONFIG_FILE
    
    @staticmethod
    def load_config() -> Dict:
        """Load configuration from file"""
        config_path = ConfigManager.get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading config: {e}")
                return {}
        return {}
    
    @staticmethod
    def save_config(config: Dict):
        """Save configuration to file"""
        config_path = ConfigManager.get_config_path()
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            os.chmod(config_path, 0o600)  # Secure the file
        except IOError as e:
            raise Exception(f"Failed to save config: {e}")
    
    @staticmethod
    def get_token() -> Optional[str]:
        """Get GitHub token from config or environment"""
        # Try environment variable first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
        
        # Try config file
        config = ConfigManager.load_config()
        return config.get('github_token')
    
    @staticmethod
    def set_token(token: str):
        """Save GitHub token to config"""
        config = ConfigManager.load_config()
        config['github_token'] = token
        ConfigManager.save_config(config)
    
    @staticmethod
    def get_model() -> str:
        """Get configured model"""
        config = ConfigManager.load_config()
        return config.get('model', 'gpt-4o')
    
    @staticmethod
    def set_model(model: str):
        """Set default model"""
        config = ConfigManager.load_config()
        config['model'] = model
        ConfigManager.save_config(config)
    
    @staticmethod
    def show_config():
        """Display current configuration"""
        config = ConfigManager.load_config()
        
        print("\n📋 Current Configuration")
        print("=" * 50)
        
        token = config.get('github_token', 'Not set')
        if token != 'Not set':
            token = token[:10] + '...' + token[-4:]
        
        print(f"GitHub Token: {token}")
        print(f"Default Model: {config.get('model', 'gpt-4o')}")
        print(f"Config File: {ConfigManager.get_config_path()}")
        print("=" * 50)