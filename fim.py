#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime

def install_watchdog():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'watchdog'])
    except Exception as e:
        print(f"Failed to install watchdog: {e}")
        sys.exit(1)

try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Watchdog not found. Attempting to install...")
    install_watchdog()
    
    # Retry imports
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

# Ensure the scripts directory is in the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config import MONITORED_DIRECTORY, BASELINE_FILE, LOG_FILE

def setup_directories():
    """
    Ensure that the monitored directory exists.
    """
    if not os.path.exists(MONITORED_DIRECTORY):
        os.makedirs(MONITORED_DIRECTORY)
        print(f"Created monitored directory: {MONITORED_DIRECTORY}")
    else:
        print(f"Monitored directory already exists: {MONITORED_DIRECTORY}")

def main():
    """
    Main function to handle command-line arguments and run the appropriate FIM functions.
    """
    parser = argparse.ArgumentParser(
        description="File Integrity Monitoring System with Real-time Detection",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["setup", "baseline", "monitor", "check"],
        help="""
        setup: Create the necessary directories
        baseline: Generate baseline hashes
        monitor: Start real-time monitoring
        check: Perform a one-time integrity check
        """
    )
    
    args = parser.parse_args()
    
    if args.command == "setup":
        # Set up the monitored directory
        setup_directories()
        print(f"FIM system set up successfully. Log file will be at: {LOG_FILE}")
        
    elif args.command == "baseline":
        # Create a new baseline
        from scripts.baseline import create_baseline
        create_baseline()
        
    elif args.command == "monitor":
        # Start real-time monitoring with Watchdog
        try:
            # Verify dependencies
            import watchdog
        except ImportError:
            print("Error: The 'watchdog' package is required for monitoring.")
            print("Please install it using: pip install watchdog")
            sys.exit(1)
            
        from scripts.monitor import start_monitoring
        start_monitoring()
        
    elif args.command == "check":
        # Perform a one-time check against the baseline
        from scripts.manual_check import perform_check
        perform_check()

if __name__ == "__main__":
    main()
