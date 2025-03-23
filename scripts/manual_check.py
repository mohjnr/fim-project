import os
import sys
import json
import logging
from datetime import datetime

# Add the parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONITORED_DIRECTORY, BASELINE_FILE, LOG_FILE
from scripts.baseline import calculate_sha256

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def perform_check():
    """
    Perform a manual integrity check against the baseline.
    
    This function provides a comprehensive comparison between the current
    state of the monitored directory and the baseline, identifying:
    - New files
    - Modified files
    - Deleted files
    
    It produces both console output and log entries for any discrepancies.
    """
    # Check if baseline exists
    if not os.path.exists(BASELINE_FILE):
        logging.error(f"Baseline file '{BASELINE_FILE}' does not exist.")
        print(f"Error: Baseline file '{BASELINE_FILE}' does not exist.")
        print(f"Please run 'python fim.py baseline' first.")
        return
        
    # Load baseline
    try:
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)
    except Exception as e:
        logging.error(f"Error loading baseline file: {e}")
        print(f"Error loading baseline file: {e}")
        return
        
    print(f"\n===== FILE INTEGRITY CHECK REPORT =====")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitored Directory: {MONITORED_DIRECTORY}")
    print(f"Baseline File: {BASELINE_FILE}")
    print("----------------------------------------")
    
    # Track results
    new_files = []
    modified_files = []
    deleted_files = []
    ok_files = []
    
    # Get current files and their states
    current_files = set()
    
    # Check for new and modified files
    for root, dirs, files in os.walk(MONITORED_DIRECTORY):
        for file in files:
            file_path = os.path.join(root, file)
            current_files.add(file_path)
            
            current_hash = calculate_sha256(file_path)
            if not current_hash:
                continue
                
            # Check if file exists in baseline
            if file_path not in baseline:
                new_files.append(file_path)
                logging.warning(f"New file detected: {file_path}")
            else:
                # Check if file has been modified
                if current_hash != baseline[file_path]["hash"]:
                    modified_files.append((file_path, baseline[file_path]["hash"], current_hash))
                    logging.warning(f"Modified file detected: {file_path}")
                else:
                    ok_files.append(file_path)
    
    # Check for deleted files
    baseline_files = set(baseline.keys())
    deleted_files = list(baseline_files - current_files)
    for file_path in deleted_files:
        logging.warning(f"Deleted file detected: {file_path}")
    
    # Print the report
    if new_files:
        print(f"\nNEW FILES ({len(new_files)}):")
        for file in new_files:
            print(f"  + {file}")
    
    if modified_files:
        print(f"\nMODIFIED FILES ({len(modified_files)}):")
        for file, old_hash, new_hash in modified_files:
            print(f"  ~ {file}")
            print(f"    Original hash: {old_hash}")
            print(f"    Current hash: {new_hash}")
    
    if deleted_files:
        print(f"\nDELETED FILES ({len(deleted_files)}):")
        for file in deleted_files:
            print(f"  - {file}")
    
    # Summary
    total_violations = len(new_files) + len(modified_files) + len(deleted_files)
    if total_violations == 0:
        print("\nNo integrity violations detected.")
        print(f"All {len(ok_files)} files match the baseline.")
    else:
        print(f"\nINTEGRITY CHECK SUMMARY:")
        print(f"  Total files checked: {len(current_files)}")
        print(f"  Files passing integrity check: {len(ok_files)}")
        print(f"  Integrity violations: {total_violations}")
        print(f"    - New files: {len(new_files)}")
        print(f"    - Modified files: {len(modified_files)}")
        print(f"    - Deleted files: {len(deleted_files)}")
    
    print("----------------------------------------")
    print(f"For detailed information, check: {LOG_FILE}")
    print("==========================================\n")
    
    # Log summary
    logging.info(f"Integrity check completed - Violations: {total_violations}, OK files: {len(ok_files)}")

if __name__ == "__main__":
    # For running the check directly
    perform_check()