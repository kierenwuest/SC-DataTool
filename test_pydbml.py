from pydbml import PyDBML

def validate_dbml(file_path):
    """
    Validates and parses the DBML file at the specified path.
    Prints debug information for successful and failed parsing.
    """
    try:
        with open(file_path, "r") as file:
            dbml_content = file.read()

        print(f"Parsing DBML file: {file_path}")
        dbml = PyDBML(dbml_content)

        print("\nDBML successfully parsed!")
        for table in dbml.tables:
            print(f"Table: {table.name}, Columns: {[col.name for col in table.columns]}")
        if dbml.refs:
            print("\nReferences:")
            for ref in dbml.refs:
                print(f"Reference: {ref}")
        if dbml.enums:
            print("\nEnums:")
            for enum in dbml.enums:
                print(f"Enum: {enum.name}, Values: {enum.items}")

    except Exception as e:
        print(f"\nError parsing DBML file: {e}")
        print(f"Error occurred at line: {e.lineno if hasattr(e, 'lineno') else 'Unknown'}")
        print(f"Error occurred at column: {e.colno if hasattr(e, 'colno') else 'Unknown'}")
        print("Ensure there are no syntax or encoding issues in the DBML file.")

if __name__ == "__main__":
    # Path to the DBML file
    dbml_file_path = "config/SC-DataModel_Schema.dbml"
    validate_dbml(dbml_file_path)
