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
            fields = [col.name for col in table.columns]
            if fields:
                queries[object_name] = f"SELECT {', '.join(fields)} FROM {object_name}"
    
    except Exception as e:
        print(f"Error parsing .dbml file with PyDBML: {e}")
    
    return queries


def query_objects(sf, soql_query):
    """
    Queries Salesforce using the given SOQL query.
    
    Args:
        sf: Salesforce connection object.
        soql_query (str): The SOQL query string.
    
    Returns:
        list: List of records returned by the query.
    """
    try:
        result = sf.query(soql_query)
        return result.get("records", [])
    except Exception as e:
        print(f"Error querying Salesforce: {e}")
        return []
