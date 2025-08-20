import streamlit as st
import json
import os

# MUST be the first Streamlit command
st.set_page_config(layout="wide")

st.header("Big JSON File Reader")
st.info("Reading sample data from downloaded big.json file")

# Define local file path
local_json_file = "big.json"

# Check if file exists
if os.path.exists(local_json_file):
    st.success(f"Found local file: {local_json_file}")
    
    # Get file size
    file_size = os.path.getsize(local_json_file)
    st.info(f"File size: {file_size / (1024*1024):.2f} MB")
    
    try:
        # Read and parse JSON file
        st.subheader("Reading JSON file...")
        with open(local_json_file, 'r', encoding='utf-8') as f:
            # Read first 10KB to get a sample
            sample_content = f.read(10240)
            
        st.success("Successfully read sample content from JSON file")
        
        # Try to parse as JSON
        try:
            # Parse the sample content
            sample_data = json.loads(sample_content)
            st.success("Successfully parsed JSON sample")
            
            # Display sample data structure
            st.subheader("Sample Data Structure")
            st.json(sample_data)
            
            # Show data type information
            st.subheader("Data Analysis")
            if isinstance(sample_data, dict):
                st.write(f"**Type:** Dictionary with {len(sample_data)} keys")
                st.write("**Keys:**", list(sample_data.keys())[:10])  # Show first 10 keys
            elif isinstance(sample_data, list):
                st.write(f"**Type:** List with {len(sample_data)} items")
                if len(sample_data) > 0:
                    st.write("**First item type:**", type(sample_data[0]).__name__)
            else:
                st.write(f"**Type:** {type(sample_data).__name__}")
                
        except json.JSONDecodeError as e:
            st.warning("Could not parse as complete JSON, showing raw content")
            st.code(sample_content[:1000] + "..." if len(sample_content) > 1000 else sample_content)
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        
else:
    st.error(f"Local file not found: {local_json_file}")
    st.info("Make sure the startup script successfully downloaded the file from Volume")

# Show file download status
st.subheader("File Download Status")
if os.path.exists(local_json_file):
    st.success("File was successfully downloaded from Volume")
    st.info("This proves the Volume access and file download workflow is working!")
else:
    st.error("File download failed or file not found")
    st.info("Check the startup logs for download errors")
