from pydbml import PyDBML

def generate_soql_from_dbml(dbml_file_path):
    """
    Parses a .dbml file using the PyDBML library and generates SOQL queries for Salesforce objects.
    
    Args:
        dbml_file_path (str): Path to the .dbml file.
    
    Returns:
        dict: A dictionary with object names as keys and SOQL queries as values.
    """
    queries = {}
    try:
        # Parse the .dbml file
        with open(dbml_file_path, "r") as file:
            dbml_content = file.read()
        
        dbml = PyDBML(dbml_content)

        # Iterate through tables and construct SOQL queries
        for table in dbml.tables:
            object_name = table.name
            soql_fields = []

            # Inspect columns to build the field list
            for col in table.columns:
                # Always include the field itself
                soql_fields.append(col.name)

                # Use `get_refs()` to check for relationships
                refs = col.get_refs()
                for ref in refs:
                    # Extract the source field (col1) and target table (table2)
                    source_field = ref.col1[0].name if ref.col1 and isinstance(ref.col1, list) else None
                    referenced_table = ref.table2.name if ref.table2 else None

                    if source_field and referenced_table:
                        if source_field.endswith("__c"):
                            # Custom relationship field: replace __c with __r
                            custom_relationship = source_field.replace("__c", "__r")
                            soql_fields.append(f"{custom_relationship}.Name")
                        else:
                            # Standard relationship field
                            soql_fields.append(f"{referenced_table}.Name")

            # Check for a custom filter in the table's note attribute
            filter_clause = None
            if table.note and str(table.note).startswith("WHERE"):
                filter_clause = str(table.note).strip()

            # Build SOQL query for the table
            if soql_fields:
                soql_query = f"SELECT {', '.join(soql_fields)} FROM {object_name}"
                if filter_clause:
                    soql_query += f" {filter_clause}"
                queries[object_name] = soql_query
    
    except Exception as e:
        print(f"Error parsing .dbml file with PyDBML: {e}")
    
    return queries


def query_objects(sf, soql_query):
    """
    Executes a SOQL query against the Salesforce API.

    Args:
        sf (Salesforce): The Salesforce connection object.
        soql_query (str): The SOQL query to execute.

    Returns:
        list: The query result records.

    Raises:
        Exception: If the query fails or an error response is returned.
    """
    try:
        response = sf.query(soql_query)
        if not response or 'records' not in response:
            raise Exception(f"Invalid response structure: {response}")
        return response['records']
    except Exception as e:
        raise Exception(f"Error querying Salesforce: {e}")
