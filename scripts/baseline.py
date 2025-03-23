import os
import hashlib
import json
import logging
from datetime import datetime
import sys

# Add the parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONITORED_DIRECTORY, BASELINE_FILE, LOG_FILE

# Configure logging to record events and errors
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_sha256(file_path):
    """
    Calculate the SHA-256 hash for a given file.
    Reads the file in 4KB chunks to handle large files efficiently.
    
    This approach ensures we don't load entire files into memory,
    making it suitable for large files while maintaining security.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks of 4KB
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

def create_baseline():
    """
    Walk through the monitored directory and generate a baseline mapping
    file paths to their SHA-256 hashes and metadata. 
    
    The baseline includes:
    - File path
    - SHA-256 hash
    - File size
    - Last modification time
    - Creation time (where available)
    
    This comprehensive approach helps in detecting various types of changes.
    """
    baseline = {}
    if not os.path.exists(MONITORED_DIRECTORY):
        logging.error(f"Monitored directory '{MONITORED_DIRECTORY}' does not exist.")
        print(f"Error: Monitored directory '{MONITORED_DIRECTORY}' does not exist.")
        return
    
    print(f"Creating baseline for files in {MONITORED_DIRECTORY}...")
    file_count = 0
    
    for root, dirs, files in os.walk(MONITORED_DIRECTORY):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_sha256(file_path)
            
            if file_hash:
                # Get file stats for additional integrity verification
                file_stat = os.stat(file_path)
                
                # Store comprehensive file information
                baseline[file_path] = {
                    "hash": file_hash,
                    "size": file_stat.st_size,
                    "modified_time": file_stat.st_mtime,
                    "created_time": file_stat.st_ctime,
                    "baseline_date": datetime.now().isoformat()
                }
                file_count += 1
                
                # Print progress for large directories
                if file_count % 100 == 0:
                    print(f"Processed {file_count} files...")
    
    try:
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline, f, indent=4)
        
        logging.info(f"Baseline created with {file_count} files and stored in '{BASELINE_FILE}'.")
        print(f"Baseline successfully created with {file_count} files and stored in '{BASELINE_FILE}'.")
    except Exception as e:
        logging.error(f"Error writing baseline file: {e}")
        print(f"Error writing baseline file: {e}")

if __name__ == "__main__":
    create_baseline()