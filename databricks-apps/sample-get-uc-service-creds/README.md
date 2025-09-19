# Databricks Unity Catalog Service Credentials - APP Example

A simple Databricks Streamlit app demonstrating how to use Databricks Unity Catalog service credentials to access AWS resources.

## What it does

This example shows how to:
1. Get temporary AWS credentials from a Databricks Unity Catalog service credential
2. Use those credentials to list EC2 instances in a specified AWS region
3. Display the results in a simple web interface

## Prerequisites

- Databricks Unity Catalog service credential configured with EC2 read permissions
- The service credential should have an IAM role with `ec2:DescribeInstances` permission

## Usage

1. Enter your Databricks service credential name in the sidebar
2. Select an AWS region
3. Click "Fetch EC2 Instances" to see the results

## Files

- `app.py` - Main Streamlit application
- `app.yaml` - Databricks Apps configuration
- `requirements.txt` - Python dependencies

## Running

```bash
streamlit run app.py
```

The app will display EC2 instance names and IDs from the selected region using credentials obtained from your Databricks Unity Catalog service credential.
