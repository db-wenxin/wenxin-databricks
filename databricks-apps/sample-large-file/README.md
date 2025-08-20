# Large File Handling in Databricks Apps



## Problem Statement

**I want to run an App that needs to use/load a file that is larger than 10 MB**

We are able to use CLI/SDK to create/sync a single file to workspace, however the App deployment failed because it could not process this large file.

```
Failed to snapshot source code due to error: File /Workspace/Users/xxxxxx/big.json is larger than the maximum allowed file size of 10485760 bytes. Please reduce the file size and try again.
```

## Solutions

### Solution 1: use other VCS backed App to bypass the workspace filesystem
*As of today Aug, 2025, this feature has not been released yet*

### Solution 2: Use Databricks Volume or AWS S3 to store the large file and load the file into the app container after the app is running
    - Download the file as part of an App startup process using Databricks, AWS, or other cloud provider APIs/SDKs.
    - If the file is required for the app to start, you may need to first download it in `app.yaml` before starting the app.

## This Demo Implementation

This repository demonstrates **Solution 2** by implementing a Databricks App that:

1. **Stores large files in Unity Catalog Volume**: The `big.json` file (18MB) is stored in `/Volumes/example/default/test-volume/`
2. **Downloads files at runtime**: Uses a startup script to download the file before the main app starts
3. **Processes large files locally**: The Streamlit app reads and displays sample data from the downloaded file

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Unity Catalog │    │   Databricks App │    │   Streamlit App │
│     Volume      │    │   Container      │    │                 │
│                 │    │                  │    │                 │
│ big.json (18MB) │───▶│ startup.py       │───▶│ app.py          │
│                 │    │ (downloads file) │    │ (reads file)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## File Structure

```
sample-large-file/
├── app.yaml          # Databricks App configuration
├── startup.py        # Startup script that downloads file from Volume
├── app.py           # Streamlit main application
├── requirements.txt # Python dependencies
├── create_dummy.py  # Script to create test data
└── README.md       # This documentation
```

## Configuration

### Customizing Volume Path and File Settings

The `startup.py` script includes configurable parameters at the top of the file for easy customization:

```python
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
```

**To customize for your environment:**

1. **Update Volume settings**:
   - `VOLUME_CATALOG`: Your Unity Catalog catalog name
   - `VOLUME_SCHEMA`: Your Unity Catalog schema name
   - `VOLUME_NAME`: Your Unity Catalog volume name
   - `FILE_NAME`: The name of your large file

2. **Update Local settings**:
   - `LOCAL_FILE_PATH`: Where to save the file locally (relative to app directory)

**Example configuration for a different environment:**
```python
VOLUME_CATALOG = "my-catalog"        # Your catalog
VOLUME_SCHEMA = "my-schema"          # Your schema
VOLUME_NAME = "my-volume"            # Your volume
FILE_NAME = "large-model.pkl"        # Your file
LOCAL_FILE_PATH = "model.pkl"        # Local filename
```

### app.yaml
```yaml
command: [
  "python",
  "startup.py"
]
```

This configuration tells Databricks to run `startup.py` instead of directly running Streamlit, allowing us to download the large file before the app starts.

## Workflow

### 1. Startup Phase (`startup.py`)
- Uses Databricks SDK to download the configured file from the specified Volume path
- Falls back to `dbutils` if SDK is not available
- Starts Streamlit app after successful download

### 2. Application Phase (`app.py`)
- Checks if the downloaded file exists locally
- Reads and parses file content
- Displays file size, data structure, and sample data

## Testing

To test the download functionality, you can run the startup script directly:
```bash
python startup.py
```

## Creating Large Test Files

To create a large JSON file for testing:
```python
import json

data = [{"id": i, "text": "dummy text"} for i in range(500000)]  # 18MB
with open("big.json", "w") as f:
    json.dump(data, f)
```

## Key Benefits

- ✅ **Bypasses 10MB file size limit**: Files are downloaded at runtime, not during deployment
- ✅ **Uses existing Databricks infrastructure**: Leverages Unity Catalog Volumes
- ✅ **Flexible file handling**: Supports both Databricks SDK and dbutils
- ✅ **Production ready**: Includes error handling and fallback mechanisms
- ✅ **Easy configuration**: Simple parameter-based customization

## Dependencies

- `streamlit==1.38.0`
- `databricks-sdk>=0.12.0`

## Deployment

Follow the [Databricks Apps deployment documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy) to deploy this app.

## Use Cases

This pattern is useful for:
- Machine learning models that require large model files
- Data processing apps that need large reference datasets
- Applications that work with large configuration files
- Any scenario where files exceed the 10MB deployment limit

## Important Notes

### Pre-configured Permissions Required

The following components must be pre-configured outside of this application:

1. **Unity Catalog Volume**: The Volume specified in your configuration must exist and be accessible
2. **Large File**: The file specified in `FILE_NAME` must be uploaded to the Volume before running the app
3. **App Permissions**: The Databricks App must have proper permissions to:
   - Access the Unity Catalog Volume
   - Read files from the Volume
   - Use the Databricks SDK or dbutils

### Setup Steps (External to App)

1. **Create Unity Catalog Volume** (if not exists):
   ```sql
   CREATE VOLUME IF NOT EXISTS your-catalog.your-schema.your-volume;
   ```

2. **Upload large file to Volume**:
   ```python
   # Using Databricks SDK
   from databricks.sdk import WorkspaceClient
   w = WorkspaceClient()
   
   volume_path = f"/Volumes/your-catalog/your-schema/your-volume/your-file"
   with open("your-file", "rb") as f:
       w.files.upload(volume_path, f)
   ```

3. **Configure App Permissions**:
   - Ensure the app service principal has `READ` access to the Volume
   - Grant necessary permissions for Unity Catalog access

4. **Update Configuration**:
   - Modify the parameters in `startup.py` to match your Volume and file names

The application code assumes these external configurations are already in place.
