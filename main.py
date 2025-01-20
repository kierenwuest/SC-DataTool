import json
from salesforce.auth import get_salesforce_connection
from salesforce.queries import query_objects
from sheets.manager import create_workbook
import os

def main():
    # Load configuration and queries
    with open("config/config.json") as config_file:
        config = json.load(config_file)

    with open("config/queries.json") as queries_file:
        queries = json.load(queries_file)

    # Authenticate with Salesforce
    sf = get_salesforce_connection(config["org_alias"])

    if not sf:
        print("Failed to connect to Salesforce.")
        return

    # Query data for all objects
    workbook_data = {}
    for object_name, soql_query in queries.items():
        data = query_objects(sf, soql_query)
        if data:
            workbook_data[object_name] = data

    # Create and save the workbook
    output_file = os.path.join(os.getcwd(), "SalesforceData.xlsx")
    create_workbook(workbook_data, output_file)

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
