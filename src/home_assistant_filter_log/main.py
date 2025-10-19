"""Main CLI module for home-assistant-filter-log."""

import argparse
import json
import re
import sys
from typing import Optional, Dict, Any, List


def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a Home Assistant log line.
    
    Format: 2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info
    
    Returns a dict with:
    - timestamp: str
    - level: str (INFO, WARNING, ERROR, etc.)
    - thread: str
    - logger: str
    - message: str
    
    Returns None if the line doesn't match the expected format.
    """
    # Pattern to match Home Assistant log format
    # Example: 2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+(\w+)\s+\(([^)]+)\)\s+\[([^\]]+)\]\s+(.*)$'
    
    match = re.match(pattern, line)
    if not match:
        return None
    
    timestamp, level, thread, logger, message = match.groups()
    
    return {
        "timestamp": timestamp,
        "level": level,
        "thread": thread,
        "logger": logger,
        "message": message
    }


def filter_logs(log_file: str, logger_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Filter log entries from a Home Assistant log file.
    
    Args:
        log_file: Path to the log file or "-" for stdin
        logger_filter: Optional logger name to filter by (e.g., "blueprint.test")
    
    Returns:
        List of parsed log entries as dictionaries
    """
    entries = []
    
    # Read from stdin or file
    if log_file == "-":
        lines = sys.stdin.readlines()
    else:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{log_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Parse and filter lines
    for line in lines:
        line = line.rstrip('\n\r')
        if not line:
            continue
        
        entry = parse_log_line(line)
        if entry is None:
            continue
        
        # Apply logger filter if specified
        if logger_filter is None or entry['logger'] == logger_filter:
            entries.append(entry)
    
    return entries


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Filter and convert Home Assistant log files to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Filter logs by logger name
  home-assistant-filter-log home-assistant.log --logger blueprint.test
  
  # Read from stdin
  cat home-assistant.log | home-assistant-filter-log - --logger homeassistant.core
  
  # Get all logs as JSON
  home-assistant-filter-log home-assistant.log
        """
    )
    
    parser.add_argument(
        'log_file',
        help='Path to the log file (use "-" for stdin)'
    )
    
    parser.add_argument(
        '--logger', '-l',
        dest='logger_filter',
        help='Filter by logger name (e.g., "blueprint.test")'
    )
    
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty-print JSON output'
    )
    
    args = parser.parse_args()
    
    # Filter logs
    entries = filter_logs(args.log_file, args.logger_filter)
    
    # Output as JSON
    if args.pretty:
        print(json.dumps(entries, indent=2))
    else:
        print(json.dumps(entries))


if __name__ == "__main__":
    main()
