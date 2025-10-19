"""Tests for the main module."""

import tempfile
import os
from home_assistant_filter_log.main import parse_log_line, filter_logs


class TestParseLogLine:
    """Tests for parse_log_line function."""
    
    def test_parse_valid_log_line(self):
        """Test parsing a valid log line."""
        line = "2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info"
        result = parse_log_line(line)
        
        assert result is not None
        assert result['timestamp'] == "2025-10-19 14:15:38.498"
        assert result['level'] == "INFO"
        assert result['thread'] == "MainThread"
        assert result['logger'] == "blueprint.test"
        assert result['message'] == "test info"
    
    def test_parse_warning_level(self):
        """Test parsing a WARNING level log."""
        line = "2025-10-19 14:15:38.498 WARNING (MainThread) [homeassistant.core] Some warning"
        result = parse_log_line(line)
        
        assert result is not None
        assert result['level'] == "WARNING"
        assert result['logger'] == "homeassistant.core"
        assert result['message'] == "Some warning"
    
    def test_parse_error_level(self):
        """Test parsing an ERROR level log."""
        line = "2025-10-19 14:15:38.498 ERROR (Thread-1) [custom.component] Error message"
        result = parse_log_line(line)
        
        assert result is not None
        assert result['level'] == "ERROR"
        assert result['thread'] == "Thread-1"
        assert result['logger'] == "custom.component"
    
    def test_parse_multiword_message(self):
        """Test parsing a log with a longer message."""
        line = "2025-10-19 14:15:38.498 INFO (MainThread) [homeassistant.setup] Setting up component lights"
        result = parse_log_line(line)
        
        assert result is not None
        assert result['message'] == "Setting up component lights"
    
    def test_parse_invalid_line(self):
        """Test parsing an invalid log line."""
        line = "This is not a valid log line"
        result = parse_log_line(line)
        
        assert result is None
    
    def test_parse_empty_line(self):
        """Test parsing an empty line."""
        line = ""
        result = parse_log_line(line)
        
        assert result is None


class TestFilterLogs:
    """Tests for filter_logs function."""
    
    def test_filter_logs_from_file(self):
        """Test filtering logs from a file."""
        # Create a temporary log file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info\n")
            f.write("2025-10-19 14:15:39.123 WARNING (MainThread) [homeassistant.core] warning message\n")
            f.write("2025-10-19 14:15:40.456 ERROR (Thread-1) [blueprint.test] error message\n")
            temp_file = f.name
        
        try:
            # Test without filter
            results = filter_logs(temp_file)
            assert len(results) == 3
            
            # Test with filter
            results = filter_logs(temp_file, logger_filter="blueprint.test")
            assert len(results) == 2
            assert all(r['logger'] == "blueprint.test" for r in results)
            
            # Test with different filter
            results = filter_logs(temp_file, logger_filter="homeassistant.core")
            assert len(results) == 1
            assert results[0]['logger'] == "homeassistant.core"
        finally:
            os.unlink(temp_file)
    
    def test_filter_logs_empty_file(self):
        """Test filtering an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_file = f.name
        
        try:
            results = filter_logs(temp_file)
            assert len(results) == 0
        finally:
            os.unlink(temp_file)
    
    def test_filter_logs_with_invalid_lines(self):
        """Test filtering logs with some invalid lines mixed in."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info\n")
            f.write("This is an invalid line\n")
            f.write("2025-10-19 14:15:39.123 WARNING (MainThread) [homeassistant.core] warning message\n")
            f.write("\n")
            f.write("2025-10-19 14:15:40.456 ERROR (Thread-1) [blueprint.test] error message\n")
            temp_file = f.name
        
        try:
            results = filter_logs(temp_file)
            # Should only parse the 3 valid lines
            assert len(results) == 3
        finally:
            os.unlink(temp_file)
