from pydbml import PyDBML

def generate_soql_query(dbml_file_path):
    """
    Parses a .dbml file and generates SOQL queries for each table,
    including table-level filters from the note attribute.
    """
    with open(dbml_file_path, "r") as file:
        dbml_content = file.read()
    
    dbml = PyDBML(dbml_content)

    # Iterate through tables and construct SOQL queries
    for table in dbml.tables:
        object_name = table.name
        soql_fields = []

        # Debug output for table
        print(f"\nProcessing Table: {object_name}")

        # Inspect columns to build the field list
        for col in table.columns:
            # Always include the field itself
            soql_fields.append(col.name)

            # Use `get_refs()` to check for relationships
            refs = col.get_refs()
            for ref in refs:
                # Debug output for reference details
                print(f"  Column: {col.name}, Ref Details: {ref}")

                # Extract table2 (referenced table) and col2 (target field)
                referenced_table = ref.table2.name if ref.table2 else None
                source_field = ref.col1[0].name if ref.col1 and isinstance(ref.col1, list) else None

                if referenced_table and source_field:
                    # Debug output for relationship mapping
                    print(f"    Source Field: {source_field}, Referenced Table: {referenced_table}")

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
            print(f"  Found Filter in Note: {filter_clause}")

        # Generate and print the SOQL query
        if soql_fields:
            soql_query = f"SELECT {', '.join(soql_fields)} FROM {object_name}"
            if filter_clause:
                soql_query += f" {filter_clause}"
            print(f"\nSOQL Query for {object_name}:")
            print(soql_query)
            print()

# Run the SOQL query generation
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 debug_script.py <path_to_dbml_file>")
    else:
        generate_soql_query(sys.argv[1])
