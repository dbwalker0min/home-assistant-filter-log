# home-assistant-filter-log

A Python utility that filters Home Assistant log files and converts them to JSON format.

## Installation

Install with `uv` or `pip`:

```bash
uvx home-assistant-filter-log
# or
pip install home-assistant-filter-log
```

## Usage

The tool parses Home Assistant log files with the following format:

```
2025-10-19 14:15:38.498 INFO (MainThread) [blueprint.test] test info
```

### Basic Usage

```bash
# Convert all logs to JSON
home-assistant-filter-log home-assistant.log

# Filter by logger name
home-assistant-filter-log home-assistant.log --logger blueprint.test

# Pretty-print JSON output
home-assistant-filter-log home-assistant.log --logger blueprint.test --pretty

# Read from stdin
cat home-assistant.log | home-assistant-filter-log - --logger homeassistant.core
```

### Output Format

The tool outputs JSON with the following structure:

```json
[
  {
    "timestamp": "2025-10-19 14:15:38.498",
    "level": "INFO",
    "thread": "MainThread",
    "logger": "blueprint.test",
    "message": "test info"
  }
]
```

### Arguments

- `log_file`: Path to the log file (use "-" for stdin)
- `--logger`, `-l`: Filter by logger name (e.g., "blueprint.test")
- `--pretty`, `-p`: Pretty-print JSON output
