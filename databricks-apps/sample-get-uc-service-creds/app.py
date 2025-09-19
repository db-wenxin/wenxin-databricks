import os
import logging
import json
import pandas as pd
import streamlit as st

import boto3

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file, else taken from app.yaml via Apps runtime
load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", None)
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", None)
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", None)

# Initialize Workspace Client
@st.cache_resource
def get_workspace_client():
    if ENVIRONMENT == "LOCAL":
        return WorkspaceClient(
            host=DATABRICKS_HOST, token=DATABRICKS_TOKEN
        )
    else:
        return WorkspaceClient()

def get_aws_credentials(wc, service_credential_name):
    """Get AWS credentials using the specified service credential name"""
    logger.info(f"Getting AWS credentials via UC for: {service_credential_name}")
    
    try:
        # Use the correct API according to the documentation: w.credentials
        # This calls generate_temporary_service_credential method
        temp_credentials = wc.credentials.generate_temporary_service_credential(
            credential_name=service_credential_name
        )
        
        logger.info(f"Response type: {type(temp_credentials)}")
        
        # The response is a TemporaryCredentials object
        # Extract AWS credentials from the response
        if hasattr(temp_credentials, 'aws_temp_credentials'):
            aws_creds = temp_credentials.aws_temp_credentials
            
            # Convert to dict format expected by boto3
            aws_credentials = {
                "access_key_id": aws_creds.access_key_id,
                "secret_access_key": aws_creds.secret_access_key,
                "session_token": aws_creds.session_token
            }
            
            logger.info(f"Successfully obtained AWS credentials")
            return aws_credentials, None
        else:
            error_msg = "No AWS credentials found in response"
            logger.error(error_msg)
            return None, error_msg

    except Exception as e:
        error_msg = f"Error getting AWS credentials: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: ", exc_info=True)
        return None, error_msg


def get_ec2_instances(aws_credentials, region="us-east-1"):
    """Get EC2 instances using AWS credentials"""
    try:
        session = boto3.Session(
            aws_access_key_id=aws_credentials["access_key_id"],
            aws_secret_access_key=aws_credentials["secret_access_key"],
            aws_session_token=aws_credentials["session_token"],
        )
        logger.info(f"Created AWS session for region: {region}")

        ec2_client = session.client("ec2", region_name=region)
        response = ec2_client.describe_instances()
        logger.info(f"Retrieved EC2 instances from region: {region}")

        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_name = "N/A"
                # Get the Name tag
                for tag in instance.get("Tags", []):
                    if tag["Key"] == "Name":
                        instance_name = tag["Value"]
                        break
                
                instance_info = {
                    "Name": instance_name,
                    "Instance ID": instance["InstanceId"]
                }
                instances.append(instance_info)
        
        logger.info(f"Found {len(instances)} EC2 instances")
        return instances, None

    except Exception as e:
        error_msg = f"Error getting EC2 instances: {str(e)}"
        logger.error(error_msg)
        return [], error_msg


# Streamlit App
def main():
    st.set_page_config(
        page_title="Databricks UC Credentials - EC2 Instance Viewer",
        layout="wide"
    )
    
    st.title("Databricks UC Credentials - EC2 Instance Viewer")
    st.markdown("---")
    
    # Initialize workspace client
    wc = get_workspace_client()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Service credential name input
        service_credential_name = st.text_input(
            "Databricks Service Credential Name",
            value=os.getenv("DATABRICKS_SERVICE_CREDENTIAL_NAME", ""),
            help="Enter the name of your Databricks Unity Catalog service credential"
        )
        
        # AWS region selection
        selected_region = st.selectbox(
            "AWS Region",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            index=0
        )
        
        # Fetch button
        fetch_instances = st.button("Fetch EC2 Instances", type="primary")
    
    # Main content area
    if not service_credential_name:
        st.warning("Please enter a Databricks Service Credential Name in the sidebar to continue.")
        return
    
    if fetch_instances:
        with st.spinner("Getting AWS credentials from Databricks Unity Catalog..."):
            # Get AWS credentials
            aws_credentials, cred_error = get_aws_credentials(wc, service_credential_name)
            
            if cred_error:
                st.error(f"Failed to get AWS credentials: {cred_error}")
                return
            
            if not aws_credentials:
                st.error("No AWS credentials received from Databricks UC")
                return
        
        # Fetch EC2 instances
        with st.spinner(f"Fetching EC2 instances from {selected_region}..."):
            instances, ec2_error = get_ec2_instances(aws_credentials, selected_region)
            
            if ec2_error:
                st.error(f"Failed to get EC2 instances: {ec2_error}")
                return
        
        # Display results
        if not instances:
            st.info(f"No EC2 instances found in region {selected_region}")
        else:
            st.write(f"**Found {len(instances)} EC2 instance(s) in {selected_region}:**")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(instances)
            st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
