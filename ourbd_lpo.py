import mysql.connector
from mysql.connector import Error
import pandas as pd
from flask import Flask, jsonify, make_response
from rapidfuzz import fuzz, process

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host='34.0.149.91',
            database='invoice_database',
            user='root',
            password='Dev112233'
        )
        if connection.is_connected():
            print("Connected to MySQL Server:", connection.get_server_info())
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            print("Connected to database:", cursor.fetchone()[0])
            return connection
    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

def fetch_lpo_data(connection, lpo_numbers):
    query = "SELECT * FROM LPO_Details WHERE PO_NUMBER = %s"
    lpo_df = pd.DataFrame()

    try:
        cursor = connection.cursor()
        for lpo in lpo_numbers:
            cursor.execute(query, (lpo,))
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            temp_df = pd.DataFrame(results, columns=columns)
            lpo_df = pd.concat([lpo_df, temp_df], ignore_index=True)

        lpo_df.drop_duplicates(subset=['ITEM'], keep='first', inplace=True)
        return lpo_df

    except Error as e:
        print("Database error:", e)
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()

def process_data(data):
    try:
        df_delivery_notes = pd.DataFrame(data.get("deliveryNoteItems", []))
        deliveryNoteNumbers = []
        lpo_numbers = []

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

        print("Delivery Notes DataFrame:", df_delivery_notes)
        print("Delivery Note Numbers List:", deliveryNoteNumbers)
        print("LPO Numbers List:", lpo_numbers)

        connection = connect_to_mysql()
        if not connection:
            return jsonify({"error": "Failed to connect to database"}), 500

        lpo_df = fetch_lpo_data(connection, lpo_numbers)

        if lpo_df.empty:
            print("No data found for provided LPO numbers.")
            return jsonify({"error": "No data found"}), 404

        # Perform matching using RapidFuzz
        df_delivery_notes["isLpoMatched"] = "No"
        df_delivery_notes["matchedWithLpoItem"] = None

        for index, row in df_delivery_notes.iterrows():
            item_name = row.get("itemName", "")
            best_match, score, _ = process.extractOne(item_name, lpo_df["DESCRIPTION"], scorer=fuzz.ratio)
            
            if score >= 40:
                df_delivery_notes.at[index, "isLpoMatched"] = "Yes"
                df_delivery_notes.at[index, "matchedWithLpoItem"] = best_match

        print("Final DataFrame:", df_delivery_notes)

        # Convert to JSON
        # response_data = df_delivery_notes.to_dict(orient="records")
        # lpo_items = lpo_df.to_dict(orient="records")

        response_data = df_delivery_notes.to_dict(orient="records")

        lpo_df=lpo_df[['PO_NUMBER','DESCRIPTION']]
        lpo_dict = (lpo_df.groupby('PO_NUMBER')['DESCRIPTION']
            .apply(list)
            .to_dict())
        # lpo_items=lpo_df.to_dict(orient="records")
        # lpo_df.to_excel('lpo_items.xlsx')
        print(response_data)
        # Return response using make_response()
        return {
    "deliveryNoteItems": response_data,
    "lpoItems": lpo_dict
}

        

    except Exception as e:
        print("Error in processing:", e)
        return jsonify({"error": str(e)}), 500



