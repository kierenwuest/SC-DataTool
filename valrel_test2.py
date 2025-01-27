from pydbml import PyDBML

def extract_relationships_from_dbml():
    """
    Extract relationships from a DBML string for OrderItem.
    """
    dbml_str = '''
    Table Standard.OrderItem {
      OrderId integer [ref: > Standard.Order.Id]
    }

    Table Standard.Order {
      Id id [not null]
    }
    '''
    # Parse the DBML string
    dbml_content = PyDBML(dbml_str)

    # Log all parsed tables and columns
    print("Debug: Parsed tables and columns:")
    for table in dbml_content.tables:
        print(f"Table: {table.full_name}")
        for column in table.columns:
            print(f"  Column: {column.name}, Properties: {column.properties}")

    # Locate the OrderItem table
    table = next((tbl for tbl in dbml_content.tables if tbl.full_name == "Standard.OrderItem"), None)
    if not table:
        raise ValueError("Table Standard.OrderItem not found in DBML.")

    # Extract relationships
    relationships = []
    for column in table.columns:
        if "ref" in column.properties:
            ref_table, ref_column = column.properties["ref"].split(".")
            ref_table = ref_table.split(".")[-1]  # Remove schema prefix
            relationships.append((column.name, ref_table.strip(), ref_column.strip()))

    return relationships

if __name__ == "__main__":
    try:
        # Extract relationships and print
        relationships = extract_relationships_from_dbml()
        print(f"Extracted relationships: {relationships}")
    except Exception as e:
        print(f"Error: {e}")
