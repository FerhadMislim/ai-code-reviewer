"""
Tests for configuration management
"""

import unittest
import os
from pathlib import Path
from src.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_path(self):
        """Test config path generation"""
        path = ConfigManager.get_config_path()
        self.assertIsInstance(path, Path)
        self.assertTrue(str(path).endswith('.code_reviewer_config'))
    
    def test_save_and_load_token(self):
        """Test saving and loading token"""
        test_token = "test_token_12345"
        
        # Save token
        ConfigManager.set_token(test_token)
        
        # Load token
        loaded_token = ConfigManager.get_token()
        
        # Should get the token (either from env or config)
        self.assertIsNotNone(loaded_token)
    
    def test_model_configuration(self):
        """Test model configuration"""
        test_model = "gpt-4o-mini"
        
        ConfigManager.set_model(test_model)
        loaded_model = ConfigManager.get_model()
        
        self.assertEqual(loaded_model, test_model)
    
    def test_environment_variable_priority(self):
        """Test that environment variable takes priority"""
        # Set environment variable
        os.environ['GITHUB_TOKEN'] = 'env_token'
        
        token = ConfigManager.get_token()
        self.assertEqual(token, 'env_token')
        
        # Clean up
        del os.environ['GITHUB_TOKEN']


if __name__ == '__main__':
    unittest.main()