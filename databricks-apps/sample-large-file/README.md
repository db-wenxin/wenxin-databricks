# Large File Handling in Databricks Apps



## Problem Statement

**Q: My customer wants to run an App that needs to use/load a file that is larger than 10 MB**

We are able to use CLI/SDK to create/sync a single file to workspace, however the App deployment failed because it could not process this large file.

```
Failed to snapshot source code due to error: File /Workspace/Users/xxxxxx/big.json is larger than the maximum allowed file size of 10485760 bytes. Please reduce the file size and try again.
```

## Solutions

### Solution 1: Use Git-backed App
*As of today Aug 20, 2025, this feature has not been released yet*

### Solution 2: Use Databricks Volume or AWS S3 to store the large file and load the file into the app container after the app is running
If the file is required for the app to start, you may need to first download it in `app.yaml` before starting the app.

## This Demo Implementation

This repository demonstrates **Solution 2** by implementing a Databricks App that:

1. **Stores large files in Unity Catalog Volume**: The `big.json` file (18MB) is stored in `/Volumes/wenxin-test/default/test-volume/`
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
src/app/
├── app.yaml          # Databricks App configuration
├── startup.py        # Startup script that downloads file from Volume
├── app.py           # Streamlit main application
├── requirements.txt # Python dependencies
└── README.md       # This documentation
```

## Workflow

### 1. Startup Phase (`startup.py`)
- Uses Databricks SDK to download `big.json` from `/Volumes/wenxin-test/default/test-volume/big.json`
- Falls back to `dbutils` if SDK is not available
- Starts Streamlit app after successful download

### 2. Application Phase (`app.py`)
- Checks if the downloaded `big.json` file exists locally
- Reads and parses JSON content
- Displays file size, data structure, and sample data

## Configuration

### app.yaml
```yaml
command: [
  "python",
  "startup.py"
]
```

This configuration tells Databricks to run `startup.py` instead of directly running Streamlit, allowing us to download the large file before the app starts.

## Testing

Run the test script to verify download functionality:
```bash
python test_download.py
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

1. **Unity Catalog Volume**: The Volume `/Volumes/wenxin-test/default/test-volume/` (example in this case) must exist and be accessible
2. **Large JSON File**: The `big.json` file must be uploaded to the Volume before running the app
3. **App Permissions**: The Databricks App must have proper permissions to:
   - Access the Unity Catalog Volume
   - Read files from the Volume
   - Use the Databricks SDK or dbutils

### Setup Steps (External to App)

1. **Create Unity Catalog Volume** (if not exists):
   ```sql
   CREATE VOLUME IF NOT EXISTS wenxin-test.default.test-volume;
   ```

2. **Upload large file to Volume**:
   ```python
   # Using Databricks SDK
   from databricks.sdk import WorkspaceClient
   w = WorkspaceClient()
   
   with open("big.json", "rb") as f:
       w.files.upload("/Volumes/wenxin-test/default/test-volume/big.json", f)
   ```

3. **Configure App Permissions**:
   - Ensure the app service principal has `READ` access to the Volume
   - Grant necessary permissions for Unity Catalog access

The application code assumes these external configurations are already in place.
