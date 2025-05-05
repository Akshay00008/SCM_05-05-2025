import json
import re

def clean_markdown_json(raw_text):
    """Strip markdown formatting from a JSON code block, if present."""
    cleaned = re.sub(r'^```(?:json)?\s*', '', raw_text.strip())
    cleaned = re.sub(r'\s*```$', '', cleaned)
    return cleaned.strip()

def extract_details(content):
    """Extracts structured delivery details from formatted JSON string or markdown block."""
    # Attempt to extract JSON block wrapped in markdown formatting
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    json_str = None

    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to clean and parse in case it's not wrapped in markdown
        cleaned = clean_markdown_json(content)
        json_str = cleaned

    # Try parsing JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError("Could not parse valid JSON data.") from e

    # Extract front and back plate numbers
    truck_number = data.get("truck_Number", "Not provided.")
    if "/" in truck_number:
        front_plate, back_plate = truck_number.split(" / ")
    else:
        front_plate = truck_number
        back_plate = data.get("Back Plate Number", "0")

    # Build product list safely
    products = data.get("products", [])
    formatted_products = []
    for product in products:
        formatted_products.append({
            "serialNumber": product.get("serialNumber", "Not provided."),
            "productName": product.get("productName", "Not provided."),
            "quantity": product.get("quantity", "Not provided."),
            "unitPrice": product.get("unitPrice", "Not provided."),
            "totalPrice": product.get("totalPrice", "Not provided."),
            "batchNumber": product.get("batchNumber", "Not provided."),
            "lpoNumber": product.get("lpoNumber", "Not provided.")
        })

    # Final structured output
    tailored_data = {
        "deliveryNoteNumber": data.get("deliveryNoteNumber", "Not provided."),
        "lpoNumber": data.get("lpoNumber", "Not provided."),
        "driverName": data.get("driverName", "Not provided."),
        "driverContact": data.get("driverContact", "Not provided."),
        "truck_Number": truck_number,
        "tankNumber": data.get("tankNumber", "Not provided."),
        "Front Plate Number": front_plate,
        "Back Plate Number": back_plate,
        "pointOfOrigin": data.get("pointOfOrigin", "Not provided."),
        "finalDestination": data.get("finalDestination", "Not provided."),
        "portOfDischarge": data.get("portOfDischarge", "Not provided."),
        "1st weight": data.get("1st weight", "Not provided."),
        "2nd weight": data.get("2nd weight", "Not provided."),
        "Net weight": data.get("Net weight", "Not provided."),
        "countryOfFinalDestination": data.get("countryOfFinalDestination", "Not provided."),
        "products": formatted_products,
        "ocrSeals": data.get("ocrSeals", [])
    }

    return tailored_data
