import argparse
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
    # Parse arguments
    parser = argparse.ArgumentParser(description="Salesforce Data Tool")
    parser.add_argument(
        "-e", "--extract", 
        metavar="DBML_FILE", 
        help="Extract data based on the provided .dbml file",
        required=False
    )
    # Additional operations can be added here
    # parser.add_argument("--upsert", metavar="DBML_FILE", help="Upsert operation", required=False)
    args = parser.parse_args()

    if args.extract:
        dbml_file_path = os.path.join("config", args.extract)
        if not os.path.exists(dbml_file_path):
            logging.error(f"The file {dbml_file_path} does not exist.")
            return
    else:
        logging.error("No operation specified. Use --extract with a .dbml file.")
        return

    try:
        # Load configuration
        logging.info("Loading configuration...")
        with open("config/config.json") as config_file:
            config = json.load(config_file)

        # Parse .dbml file to generate SOQL queries
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
                log_data.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Error querying Salesforce",
                    f"{e}",
                    soql_query,
                    "Failure"
                ])

        # Create and save the workbook
        # Extract the base name of the .dbml file without the extension
        dbml_base_name = os.path.splitext(os.path.basename(args.extract))[0]
        # Create and save the workbook with the constructed filename
        output_file = os.path.join(os.getcwd(), f"{config['org_alias']}_{datetime.now().strftime('%Y-%m-%d')}_{dbml_base_name}.xlsx")
        logging.info("Creating workbook...")
        create_workbook(workbook_data, output_file, log_data)
        logging.info(f"Data saved to {output_file}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
