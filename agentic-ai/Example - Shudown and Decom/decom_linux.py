import os
import sys
import requests

# --- CONFIGURATION SETTINGS ---
# Replace with your actual ServiceNow instance name (e.g., 'dev12345')
SN_INSTANCE = "your_instance_name"
SN_TABLE = "cmdb_ci"  # Base CMDB table, or specific like 'cmdb_ci_server', 'cmdb_ci_computer'

# Authentication (Best practice: Use environment variables instead of hardcoding)
SN_USER = os.getenv("SNOW_USER", "your_username")
SN_PASSWORD = os.getenv("SNOW_PASSWORD", "your_password")

# --- CMDB FIELD CONFIGURATIONS ---
# Standard ServiceNow choices for decommissioned assets (adjust based on your organization's custom schema)
DECOM_PAYLOAD = {
    "operational_status": "6",    # "6" typically maps to "Operational Status: Retired / Decommissioned"
    "install_status": "7",        # "7" typically maps to "Install Status: Retired"
    "comments": "Asset marked as decommissioned via automated Python script."
}

def decommission_asset_by_sys_id(sys_id):
    """Updates a single ServiceNow CI record using its unique Sys ID."""
    url = f"https://{SN_INSTANCE}://{SN_TABLE}/{sys_id}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # Sending PATCH request to partially update the record fields
        response = requests.patch(
            url, 
            auth=(SN_USER, SN_PASSWORD), 
            headers=headers, 
            json=DECOM_PAYLOAD
        )
        
        if response.status_code == 200:
            print(f"[Success] Asset Sys ID {sys_id} has been marked as decommissioned.")
            return True
        else:
            print(f"[Error] Failed to update Sys ID {sys_id}. Status Code: {response.status_code}")
            print(f"Response Summary: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[Critical] Connection error encountered: {e}")
        return False

def query_sys_id_by_name(asset_name):
    """Finds the Sys ID of an asset using its human-readable name or asset tag."""
    # Using sysparm_query for efficient server-side filtering
    url = f"https://{SN_INSTANCE}://{SN_TABLE}"
    params = {
        "sysparm_query": f"name={asset_name}^ORasset_tag={asset_name}",
        "sysparm_limit": 1,
        "sysparm_fields": "sys_id,name"
    }
    
    try:
        response = requests.get(url, auth=(SN_USER, SN_PASSWORD), params=params)
        if response.status_code == 200:
            results = response.json().get("result", [])
            if results:
                return results[0]["sys_id"]
            print(f"[Warning] No asset found with name/tag: {asset_name}")
        return None
    except requests.exceptions.RequestException:
        return None

if __name__ == "__main__":
    # Ensure dependencies are available
    if not SN_USER or not SN_PASSWORD or SN_INSTANCE == "your_instance_name":
        print("Error: Please set up your ServiceNow instance credentials properly.")
        sys.exit(1)

    # Example Target Asset Identifier (Name, Serial Number, or Asset Tag)
    TARGET_ASSET = "SERVER-PROD-01"
    
    print(f"Locating asset record for: {TARGET_ASSET}...")
    asset_sys_id = query_sys_id_by_name(TARGET_ASSET)
    
    if asset_sys_id:
        decommission_asset_by_sys_id(asset_sys_id)
