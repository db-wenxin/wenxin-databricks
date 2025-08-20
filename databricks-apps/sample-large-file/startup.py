#!/usr/bin/env python3
"""
Startup script for Databricks App
Downloads big.json from Volume before starting Streamlit app
"""

import os
import sys
import subprocess
from pathlib import Path

# =============================================================================
# CONFIGURATION PARAMETERS - CUSTOMIZE THESE FOR YOUR ENVIRONMENT
# =============================================================================

# Volume configuration
VOLUME_CATALOG = "example"           # Your Unity Catalog catalog name
VOLUME_SCHEMA = "default"            # Your Unity Catalog schema name  
VOLUME_NAME = "test-volume"          # Your Unity Catalog volume name
FILE_NAME = "big.json"               # Name of the file to download

# Local file configuration
LOCAL_FILE_PATH = "big.json"         # Local path where file will be saved

# =============================================================================
# END CONFIGURATION - DO NOT MODIFY BELOW THIS LINE
# =============================================================================

def get_volume_path():
    """Construct the full volume path from configuration parameters"""
    return f"/Volumes/{VOLUME_CATALOG}/{VOLUME_SCHEMA}/{VOLUME_NAME}/{FILE_NAME}"

def download_file_from_volume():
    """Download file from Volume using Databricks SDK"""
    try:
        from databricks.sdk import WorkspaceClient
        
        print("Initializing Databricks SDK...")
        w = WorkspaceClient()
        
        # Define paths using configuration
        volume_file_path = get_volume_path()
        
        print(f"Downloading {volume_file_path} to {LOCAL_FILE_PATH}...")
        
        # Download file using SDK
        download_response = w.files.download(volume_file_path)
        
        print(f"Response type: {type(download_response)}")
        
        # According to Databricks SDK docs, contents_ is BinaryIO | None
        if hasattr(download_response, 'contents') and download_response.contents is not None:
            print("Response has contents attribute (BinaryIO)...")
            binary_content = download_response.contents
            print(f"Contents type: {type(binary_content)}")
            
            # Read from the BinaryIO object
            if hasattr(binary_content, 'read'):
                content = binary_content.read()
                print(f"Successfully read {len(content)} bytes from BinaryIO")
            else:
                print(f"BinaryIO object doesn't have read() method")
                return False
        elif hasattr(download_response, 'content'):
            print("Response has content attribute...")
            content = download_response.content
        elif hasattr(download_response, 'body'):
            print("Response has body attribute...")
            content = download_response.body
        elif hasattr(download_response, 'read'):
            print("Response has read() method, reading content...")
            content = download_response.read()
        else:
            print(f"Unknown response type, trying to convert to bytes...")
            try:
                content = bytes(download_response)
            except:
                print(f"Failed to convert response to bytes. Response: {download_response}")
                return False
        
        print(f"Content type: {type(content)}, length: {len(content) if content else 0}")
        
        # Write to local file
        with open(LOCAL_FILE_PATH, 'wb') as f:
            f.write(content)
        
        file_size = len(content)
        print(f"Successfully downloaded {FILE_NAME} ({file_size / (1024*1024):.2f} MB)")
        
        return True
        
    except ImportError:
        print("Databricks SDK not available, trying dbutils...")
        try:
            # Try using dbutils as fallback
            volume_path = get_volume_path()
            dbutils.fs.cp(volume_path, f"file:/{LOCAL_FILE_PATH}")
            print(f"Successfully downloaded {FILE_NAME} using dbutils")
            return True
        except Exception as e:
            print(f"dbutils download failed: {str(e)}")
            return False
    except Exception as e:
        print(f"SDK download failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def start_streamlit():
    """Start the Streamlit application"""
    print("Starting Streamlit application...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    app_py_path = script_dir / "app.py"
    
    # Start streamlit
    cmd = ["streamlit", "run", str(app_py_path)]
    print(f"Running: {' '.join(cmd)}")
    
    # Use subprocess to start streamlit
    process = subprocess.Popen(cmd)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        process.terminate()
        process.wait()

def main():
    """Main startup function"""
    print("Databricks App Startup")
    print("=" * 50)
    print(f"Configuration:")
    print(f"  Volume: /Volumes/{VOLUME_CATALOG}/{VOLUME_SCHEMA}/{VOLUME_NAME}")
    print(f"  File: {FILE_NAME}")
    print(f"  Local path: {LOCAL_FILE_PATH}")
    print("=" * 50)
    
    # Step 1: Download file from Volume
    download_success = download_file_from_volume()
    
    if download_success:
        print("File download completed successfully")
    else:
        print("File download failed, but continuing with app startup")
    
    print("-" * 50)
    
    # Step 2: Start Streamlit app
    start_streamlit()

if __name__ == "__main__":
    main()
