# File Integrity Monitoring System

A real-time file integrity monitoring system that detects and alerts on unauthorized file modifications.

## Features

- **File Baseline Creation**: Generate baseline hashes of files for comparison
- **Real-time Monitoring**: Watch for file changes in specified directories
- **Integrity Checking**: Compare current file states against the baseline
- **Alerting**: Log and notify when unauthorized changes are detected

## Requirements

- Python 3.x
- Watchdog 3.0.0

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The system supports the following commands:

### Setup Directories

```
python fim.py setup
```

Creates the necessary directories for monitoring.

### Create Baseline

```
python fim.py baseline
```

Generates baseline hashes of all files in the monitored directory.

### Start Monitoring

```
python fim.py monitor
```

Begins real-time monitoring of the specified directory.

### Check Files

```
python fim.py check
```

Performs a one-time integrity check against the baseline.

## Project Structure

- `fim.py`: Main application entry point
- `config.py`: Configuration settings
- `scripts/`: Directory containing monitoring and baseline functionality
- `monitored_files/`: Directory containing files to be monitored
- `baseline.json`: Stores baseline file hashes
- `fim_report.log`: Log file for integrity violations
