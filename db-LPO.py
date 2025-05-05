import re
import cx_Oracle
import pandas as pd  # Import pandas for DataFrame operations
from delivery_note import process_delivery_note_image
from format_conv import extract_details

# Input image path
image_path = r"C:\Users\User\OneDrive - ALGO8 AI PRIVATE LIMITED\pwani-scm\Screenshot (683).png"

# Process delivery note image and extract details
dn_data = process_delivery_note_image(image_path)
content = extract_details(dn_data)  # Creates a dictionary for the data

# Debug: Print the structure of content
print("Extracted content:", content)

try:
    # Directly access 'lpoNumber' from the dictionary
    raw_lpo_number = content.get('lpoNumber', None)
    if raw_lpo_number is None:
        raise KeyError("LPO Number not found in content")

    # Extract only the numerical part of the LPO number
    lpo_number = re.search(r'\d+', raw_lpo_number).group()
    print("Raw LPO Number:", raw_lpo_number)
    print("Extracted LPO Number:", lpo_number)

    # SQL query to fetch data for the extracted LPO number
    query = """
    SELECT
      poh.po_header_id, poh.CREATION_DATE,
      poh.type_lookup_code PO_TYPE,
      poh.authorization_status PO_STATUS,
      poh.segment1 PO_NUMBER,
      pov.vendor_name SUPPLIER_NAME,
      povs.vendor_site_code Location,
      hrls.location_code Ship_To,
      hrlb.location_code Bill_to,
      pol.line_num,
      msib.segment1 Item, msib.DESCRIPTION,
      pol.unit_price,
      pol.quantity,
      pod.amount_billed Amount,
      pod.destination_subinventory,
      ppf.full_name Buyer_Name,
      poh.closed_Code 
    FROM
      PO_HEADERS_ALL poh,
      PO_LINES_ALL pol,
      mtl_system_items_b msib,
      PO_LINE_LOCATIONS_ALL poll,
      PO_DISTRIBUTIONS_ALL pod,
      po_vendors pov,
      po_vendor_sites_All povs,
      hr_locations_all hrls,
      hr_locations_all hrlb,
      per_all_people_f ppf,
      po_line_types polt
    WHERE
      1 = 1
      AND polt.line_type_id     = pol.line_type_id
      AND povs.vendor_site_id   = poh.vendor_site_id
      AND pov.vendor_id         = poh.vendor_id
      AND pol.item_id           = msib.inventory_item_id
      AND msib.organization_id  = 84
      AND poh.po_header_id      = pol.po_header_id
      AND pol.po_line_id        = pod.po_line_id
      AND poll.line_location_id = pod.line_location_id
      AND poh.ship_to_location_id = hrls.location_id
      AND poh.bill_to_location_id = hrlb.location_id
      AND poh.agent_id          = ppf.person_id
      AND poh.segment1          = :lpo_number
    """

    # Define your TNS alias, username, and password
    dsn = "TEST"
    username = "Apps"
    password = "apps085"

    # Establish a connection to your Oracle database using the TNS alias
    try:
        connection = cx_Oracle.connect(username, password, dsn)
        cursor = connection.cursor()

        # Pass lpo_number as a parameter to the SQL query
        cursor.execute(query, lpo_number=lpo_number)
        
        # Fetch the results from the query
        results = cursor.fetchall()

        # Get column names from cursor description
        columns = [col[0] for col in cursor.description]

        # Convert results into a DataFrame
        df = pd.DataFrame(results, columns=columns)

        # Print the DataFrame
        print(df)

        # Save the DataFrame to a CSV file (optional)
        df.to_csv("lpo_details.csv", index=False)

    except cx_Oracle.DatabaseError as e:
        print("Database error:", e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
except KeyError as e:
    print(f"KeyError: {e}")
except AttributeError as e:
    print(f"AttributeError (likely missing or invalid key): {e}")
