import pandas as pd
import re
import cx_Oracle
import pandas as pd  # Import pandas for DataFrame operations
from flask import Flask, jsonify, make_response
from rapidfuzz import fuzz, process

# @app.route('/ask', methods=['POST'])
def ask(data):
       

# Simulating request.json (This will be the actual data received in a Flask API)
    data = data
    

    # Initialize empty DataFrame and lists
    df_delivery_notes = pd.DataFrame()
    deliveryNoteNumbers = []
    lpo_numbers = []
    lpo_df=pd.DataFrame()

    # Handle "delivery_notes" (Convert to DataFrame)
    if isinstance(data, dict):
        if "deliveryNoteItems" in data:
            delivery_notes_list = data["deliveryNoteItems"]
            
            if isinstance(delivery_notes_list, list):  # Ensure it's a list
                df_delivery_notes = pd.DataFrame(delivery_notes_list)

        # Handle "delivery_note_mappings" (Extract DN and LPO numbers into lists)
        if "deliveryNotes" in data:
                delivery_mappings = data["deliveryNotes"]
                
                if isinstance(delivery_mappings, list):  # Ensure it's a list
                    for item in delivery_mappings:
                        dn_value = item.get("deliveryNoteNumber", "")
                        lpo_value = item.get("lpoNumbers", "")

                        # Ensure values are always lists, even if they are single items
                        if not isinstance(dn_value, list):
                            dn_value = [dn_value]
                        if not isinstance(lpo_value, list):
                            lpo_value = [lpo_value]

                        # Extend lists with extracted values
                        deliveryNoteNumbers.extend(dn_value)
                        lpo_numbers.extend(lpo_value)

    # Print results
    print("Delivery Notes DataFrame:\n", df_delivery_notes)
    print("Delivery Note Numbers List:", deliveryNoteNumbers)
    print("LPO Numbers List:", lpo_numbers)

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
    if len(lpo_numbers) > 1 :

        for lpo in lpo_numbers :

            # Establish a connection to your Oracle database using the TNS alias
            try:
                connection = cx_Oracle.connect(username, password, dsn)
                cursor = connection.cursor()

                # Pass lpo_number as a parameter to the SQL query
                cursor.execute(query, lpo_number=lpo)
                
                # Fetch the results from the query
                results = cursor.fetchall()

                # Get column names from cursor description
                columns = [col[0] for col in cursor.description]

                # Convert results into a DataFrame
                df = pd.DataFrame(results, columns=columns)

                # Print the DataFrame
                print(df)

                lpo_df = pd.concat([lpo_df, df], ignore_index=True)

                # Save the DataFrame to a CSV file (optional)
                lpo_df.to_csv("lpo_details.csv", index=False)

            except cx_Oracle.DatabaseError as e:
                print("Database error:", e)
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
    
    else :

        # Establish a connection to your Oracle database using the TNS alias
        try:
            connection = cx_Oracle.connect(username, password, dsn)
            cursor = connection.cursor()

            # Pass lpo_number as a parameter to the SQL query
            cursor.execute(query, lpo_number=lpo_numbers)
            
            # Fetch the results from the query
            results = cursor.fetchall()

            # Get column names from cursor description
            columns = [col[0] for col in cursor.description]

            # Convert results into a DataFrame
            df = pd.DataFrame(results, columns=columns)

            # Print the DataFrame
            # print(df)

            

            # Save the DataFrame to a CSV file (optional)
            # df.to_csv("lpo_details.csv", index=False)

        except cx_Oracle.DatabaseError as e:
            print("Database error:", e)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Initialize new columns for results
    df_delivery_notes["matched"] = "No"
    df_delivery_notes["matched_value"] = None

    # Iterate through each row in df_delivery_notes
    lpo_df.drop_duplicates(subset=['ITEM'],keep='first',inplace=True)

    for index, row in df_delivery_notes.iterrows():
        item_name = row["itemName"]

        # Find best match from lpo_df["DESCRIPTION"]
        best_match, score, _ = process.extractOne(item_name, lpo_df["DESCRIPTION"], scorer=fuzz.ratio)

        # If similarity score is above threshold (e.g., 80%), mark as matched
        if score >= 40:
            df_delivery_notes.at[index, "matched"] = "Yes"
            df_delivery_notes.at[index, "matched_value"] = best_match
        else:
            df_delivery_notes.at[index, "matched"] = "No"
            df_delivery_notes.at[index, "matched_value"] = None

    # Print the final DataFrame
    print(df_delivery_notes)
    response_data = df_delivery_notes.to_dict(orient="records")

    # lpo_items=lpo_df.to_dict(orient="records")
    lpo_df=lpo_df[['PO_NUMBER','DESCRIPTION']]
    lpo_dict = (lpo_df.groupby('PO_NUMBER')['DESCRIPTION']
            .apply(list)
            .to_dict())
    print(response_data)
    return {
    "deliveryNoteItems": response_data,
    "lpoItems": lpo_dict
}
    # Return response using make_response()
    # return (response_data,lpo_items)
    
