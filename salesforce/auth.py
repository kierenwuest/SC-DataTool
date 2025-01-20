from simple_salesforce import Salesforce
import subprocess
import json

def get_salesforce_connection(org_alias):
    try:
        result = subprocess.run(
            ["sf", "org", "display", "-o", org_alias, "--json"],
            text=True,
            capture_output=True,
            check=True,
        )
        auth_details = json.loads(result.stdout)
        return Salesforce(
            instance_url=auth_details["result"]["instanceUrl"],
            session_id=auth_details["result"]["accessToken"]
        )
    except Exception as e:
        print(f"Error authenticating with Salesforce: {e}")
        return None
