from openpyxl import Workbook

def create_workbook(data, filename):
    workbook = Workbook()

    for sheet_name, records in data.items():
        # Create a new sheet or get the existing one
        if sheet_name not in workbook.sheetnames:
            sheet = workbook.create_sheet(title=sheet_name)
        else:
            sheet = workbook[sheet_name]

        if records:
            # Extract headers (keys of the first record)
            headers = list(records[0].keys())
            sheet.append(headers)

            # Append rows of data, flattening nested structures
            for record in records:
                flattened_row = [
                    str(value) if isinstance(value, (dict, list, tuple)) else value
                    for value in record.values()
                ]
                sheet.append(flattened_row)

    workbook.save(filename)
    print(f"Workbook saved to {filename}")
