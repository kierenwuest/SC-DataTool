import json
import logging
import os
from datetime import datetime
from salesforce.auth import get_salesforce_connection
from salesforce.queries import query_objects, generate_soql_from_dbml
from sheets.manager import create_workbook

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    try:
        # Load configuration
        logging.info("Loading configuration...")
        with open("config/config.json") as config_file:
            config = json.load(config_file)

        # Parse .dbml file to generate SOQL queries
        dbml_file_path = "config/SC-DataModel_Schema.dbml"
        logging.info(f"Generating SOQL queries from {dbml_file_path} using PyDBML...")
        queries = generate_soql_from_dbml(dbml_file_path)

        if not queries:
            logging.error("No valid queries generated from the .dbml file.")
            return

        # Authenticate with Salesforce
        logging.info(f"Authenticating with Salesforce org {config['org_alias']}...")
        sf = get_salesforce_connection(config["org_alias"])

        if not sf:
            logging.error("Failed to connect to Salesforce.")
            return

        # Prepare data structures for the workbook
        workbook_data = {}
        log_data = [
            ["Time", "Action", "Details", "Artifact", "Outcome"]
        ]

        # Query data for all objects
        logging.info(f"Querying data from Salesforce org {config['org_alias']}...")
        for object_name, soql_query in queries.items():
            try:
                # Log query start
                log_data.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Run Query",
                    f"On {object_name}",
                    soql_query,
                    "In Progress"
                ])

                # Execute query
                # logging.info(f"Running query for {object_name}...")
                data = query_objects(sf, soql_query)

                if data:
                    logging.info(f"Retrieved {len(data)} records for {object_name}.")
                    workbook_data[object_name] = data

                    # Update log for success
                    log_data.append([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Retrieve Records",
                        f"Retrieved {len(data)} records for {object_name}",
                        f"Sheet {object_name} in Workbook",
                        "Success"
                    ])
                else:
                    logging.warning(f"No data retrieved for {object_name}.")
                    log_data.append([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Retrieve Records",
                        f"No records retrieved for {object_name}",
                        "",
                        "No Data"
                    ])
            except Exception as e:
                logging.error(f"Error querying {object_name}: {e}")
                # Log error
                log_data.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Error querying Salesforce",
                    f"{e}",
                    soql_query,
                    "Failure"
                ])

        # Create and save the workbook
        output_file = os.path.join(os.getcwd(), f"{config['org_alias']}_{datetime.now().strftime('%Y-%m-%d')}_Data.xlsx")
        logging.info("Creating workbook...")
        create_workbook(workbook_data, output_file, log_data)
        logging.info(f"Data saved to {output_file}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
