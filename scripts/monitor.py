import os
import sys
import time
import json
import hashlib
import logging
from datetime import datetime
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# Add the parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONITORED_DIRECTORY, BASELINE_FILE, LOG_FILE

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global variable to store the baseline
baseline = {}

def load_baseline():
    """
    Load the baseline file containing file hashes and metadata.
    
    This function is critical as it provides the reference point
    against which all file changes are compared.
    """
    global baseline
    try:
        if not os.path.exists(BASELINE_FILE):
            logging.error(f"Baseline file '{BASELINE_FILE}' does not exist.")
            print(f"Error: Baseline file '{BASELINE_FILE}' does not exist.")
            print(f"Please run 'python scripts/baseline.py' first.")
            sys.exit(1)
            
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)
            
        logging.info(f"Baseline loaded with {len(baseline)} files.")
        print(f"Baseline loaded with {len(baseline)} files.")
    except Exception as e:
        logging.error(f"Error loading baseline file: {e}")
        print(f"Error loading baseline file: {e}")
        sys.exit(1)

def calculate_sha256(file_path):
    """
    Calculate the SHA-256 hash for a given file.
    Identical to the function in baseline.py to ensure consistency.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

class FileChangeHandler(FileSystemEventHandler):
    """
    Custom event handler for file system events.
    
    This class defines how the system responds to various file events:
    - File creation
    - File modification
    - File deletion
    - File movement
    
    Each event triggers appropriate integrity verification.
    """
    
    def on_created(self, event):
        """Handle file/directory creation events."""
        if event.is_directory:
            logging.info(f"New directory created: {event.src_path}")
            print(f"[NEW DIRECTORY] {event.src_path}")
        else:
            logging.warning(f"New file created: {event.src_path}")
            print(f"[NEW FILE] {event.src_path}")
            
            # Calculate hash for the new file
            file_hash = calculate_sha256(event.src_path)
            if file_hash:
                # Check if this file was in our baseline but with a different path (renamed/moved)
                found_match = False
                for path, info in baseline.items():
                    if path != event.src_path and info.get("hash") == file_hash:
                        logging.warning(f"File appears to be moved from {path} to {event.src_path}")
                        print(f"[MOVED FILE] From {path} to {event.src_path}")
                        found_match = True
                        break
                
                if not found_match:
                    logging.warning(f"New file hash: {file_hash}")
                    print(f"[INTEGRITY WARNING] New file not in baseline")
    
    def on_deleted(self, event):
        """Handle file/directory deletion events."""
        if event.is_directory:
            logging.info(f"Directory deleted: {event.src_path}")
            print(f"[DELETED DIRECTORY] {event.src_path}")
        else:
            if event.src_path in baseline:
                logging.warning(f"Baseline file deleted: {event.src_path}")
                print(f"[INTEGRITY VIOLATION] Baseline file deleted: {event.src_path}")
            else:
                logging.info(f"Non-baseline file deleted: {event.src_path}")
                print(f"[DELETED FILE] {event.src_path} (not in baseline)")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return  # Directory modifications are not as relevant
            
        if event.src_path in baseline:
            # Calculate new hash and compare with baseline
            new_hash = calculate_sha256(event.src_path)
            if new_hash and new_hash != baseline[event.src_path]["hash"]:
                logging.warning(f"File modified: {event.src_path}")
                logging.warning(f"Original hash: {baseline[event.src_path]['hash']}")
                logging.warning(f"New hash: {new_hash}")
                
                print(f"[INTEGRITY VIOLATION] File modified: {event.src_path}")
                print(f"  Original hash: {baseline[event.src_path]['hash']}")
                print(f"  New hash: {new_hash}")
        else:
            # Modification of a file not in our baseline
            logging.info(f"Modified file not in baseline: {event.src_path}")
            print(f"[MODIFIED FILE] {event.src_path} (not in baseline)")
    
    def on_moved(self, event):
        """Handle file/directory movement/renaming events."""
        if event.is_directory:
            logging.info(f"Directory moved from {event.src_path} to {event.dest_path}")
            print(f"[MOVED DIRECTORY] From {event.src_path} to {event.dest_path}")
        else:
            if event.src_path in baseline:
                logging.warning(f"Baseline file moved from {event.src_path} to {event.dest_path}")
                print(f"[INTEGRITY ALERT] Baseline file moved: {event.src_path} → {event.dest_path}")
            else:
                logging.info(f"Non-baseline file moved from {event.src_path} to {event.dest_path}")
                print(f"[MOVED FILE] From {event.src_path} to {event.dest_path} (not in baseline)")

def start_monitoring():
    """
    Start real-time monitoring of the specified directory using Watchdog.
    
    This function sets up the observer pattern to watch for file system
    events and respond accordingly. It runs continuously until interrupted.
    """
    # Load the baseline for comparison
    load_baseline()
    
    # Check if monitored directory exists
    if not os.path.exists(MONITORED_DIRECTORY):
        logging.error(f"Monitored directory '{MONITORED_DIRECTORY}' does not exist.")
        print(f"Error: Monitored directory '{MONITORED_DIRECTORY}' does not exist.")
        sys.exit(1)
    
    # Set up the event handler and observer
    event_handler = FileChangeHandler()
    observer = Observer()
    
    # Schedule the observer to watch the directory recursively
    observer.schedule(event_handler, MONITORED_DIRECTORY, recursive=True)
    
    # Start the observer
    observer.start()
    
    try:
        logging.info(f"Started real-time monitoring of {MONITORED_DIRECTORY}")
        print(f"Started real-time monitoring of {MONITORED_DIRECTORY}")
        print("Press Ctrl+C to stop monitoring...")
        
        # Keep the main thread running to receive events
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        observer.stop()
        logging.info("Monitoring stopped by user.")
        print("\nMonitoring stopped by user.")
    
    # Wait for the observer to finish
    observer.join()

if __name__ == "__main__":
    start_monitoring()