#!/usr/bin/env python3
"""
Basic tests for the autonomous agent.
Tests the core functionality without requiring API calls.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from autonomous_agent import AutonomousAgent


class TestAutonomousAgent(unittest.TestCase):
    """Test cases for AutonomousAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = AutonomousAgent()
    
    def test_initialization(self):
        """Test agent initialization with default parameters."""
        self.assertEqual(self.agent.model, "deepseek-ai/DeepSeek-R1-0528-Turbo")
        self.assertEqual(self.agent.api_url, "https://api.deepinfra.com/v1/openai/chat/completions")
        self.assertIn("X-Deepinfra-Source", self.agent.headers)
    
    def test_custom_model_initialization(self):
        """Test agent initialization with custom model."""
        custom_agent = AutonomousAgent(model="custom-model")
        self.assertEqual(custom_agent.model, "custom-model")
    
    @patch('autonomous_agent.r.post')
    def test_query_non_streaming(self, mock_post):
        """Test non-streaming query."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.agent.query("Test prompt", stream=False)
        
        self.assertEqual(result, 'Test response')
        mock_post.assert_called_once()
    
    @patch('autonomous_agent.r.post')
    def test_query_streaming(self, mock_post):
        """Test streaming query."""
        # Mock streaming response
        mock_response = Mock()
        mock_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{"content":" World"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines.return_value = mock_lines
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch('builtins.print'):
            result = self.agent.query("Test prompt", stream=True)
        
        self.assertEqual(result, 'Hello World')
        mock_post.assert_called_once()
    
    @patch('autonomous_agent.r.post')
    def test_query_error_handling(self, mock_post):
        """Test error handling in query."""
        mock_post.side_effect = Exception("API Error")
        
        result = self.agent.query("Test prompt")
        
        self.assertIsNone(result)
    
    def test_handle_stream_empty(self):
        """Test stream handling with empty response."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = []
        
        with patch('builtins.print'):
            result = self.agent._handle_stream(mock_response)
        
        self.assertEqual(result, '')
    
    def test_handle_stream_with_content(self):
        """Test stream handling with content."""
        mock_response = Mock()
        mock_lines = [
            b'data: {"choices":[{"delta":{"content":"Test"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines.return_value = mock_lines
        
        with patch('builtins.print'):
            result = self.agent._handle_stream(mock_response)
        
        self.assertEqual(result, 'Test')
    
    @patch.object(AutonomousAgent, 'query')
    def test_research_method(self, mock_query):
        """Test research method."""
        mock_query.return_value = "Research results"
        
        result = self.agent.research("quantum computing")
        
        self.assertIsNotNone(result)
        mock_query.assert_called_once()
    
    @patch.object(AutonomousAgent, 'query')
    def test_generate_code_method(self, mock_query):
        """Test generate_code method."""
        mock_query.return_value = "def hello(): pass"
        
        result = self.agent.generate_code("write a hello function")
        
        self.assertIsNotNone(result)
        mock_query.assert_called_once()
    
    @patch.object(AutonomousAgent, 'query')
    def test_write_method(self, mock_query):
        """Test write method."""
        mock_query.return_value = "Written content"
        
        result = self.agent.write("AI benefits")
        
        self.assertIsNotNone(result)
        mock_query.assert_called_once()
    
    @patch.object(AutonomousAgent, 'query')
    def test_analyze_method(self, mock_query):
        """Test analyze method."""
        mock_query.return_value = "Analysis results"
        
        result = self.agent.analyze("Some content to analyze")
        
        self.assertIsNotNone(result)
        mock_query.assert_called_once()
    
    @patch.object(AutonomousAgent, 'query')
    def test_parse_and_execute(self, mock_query):
        """Test parse_and_execute method."""
        mock_query.return_value = "Task completed"
        
        with patch('builtins.print'):
            result = self.agent.parse_and_execute("Do something")
        
        self.assertIsNotNone(result)
        mock_query.assert_called_once()


class TestCompactVersion(unittest.TestCase):
    """Test the compact version code structure."""
    
    def test_compact_imports(self):
        """Test that compact version imports work."""
        try:
            import requests as r
            import json
            self.assertTrue(True)
        except ImportError:
            self.fail("Required imports for compact version not available")
    
    def test_walrus_operator(self):
        """Test that walrus operator works (Python 3.8+)."""
        # Test walrus operator assignment
        # The value 6 represents the length of "data: " prefix in SSE format
        SSE_PREFIX_LEN = 6
        test_value = "data: test"
        if (c := test_value[SSE_PREFIX_LEN:]) != "[DONE]":
            self.assertEqual(c, "test")


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Running Tests for Autonomous Agent")
    print("=" * 60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestCompactVersion))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
