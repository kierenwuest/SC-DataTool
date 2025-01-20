def query_objects(sf, soql_query):
    try:
        result = sf.query(soql_query)
        return result.get("records", [])
    except Exception as e:
        print(f"Error querying Salesforce: {e}")
        return []