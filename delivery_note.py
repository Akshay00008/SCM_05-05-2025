import os
import base64
import json
from openai import OpenAI
from fpdf import FPDF
from pdf2image import convert_from_path

os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI()

class DeliveryNoteTextExtractor:
    def __init__(self, api_key):
        api_key="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"
        OpenAI.api_key = api_key
        

    def extract_text(self,image_path):
        try:
            if image_path.lower().endswith(".pdf"):
                image_path = self.convert_pdf_to_image(image_path)

            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

            # response = client.chat.completions.create(
            #     model='gpt-4o',
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": (
            #                 "You are an information extraction assistant. Extract the requested fields from the delivery note "
            #                 "and return the output ONLY in the exact following JSON structure. Do not add any commentary, explanation, or extra text."
            #             )
            #         },
            #         {
            #             "role": "user",
            #             "content": [
            #                 {"type": "text", "text": "Extract the following details from the delivery note image."},
            #                 {"type": "text", "text": "Required fields:"},
            #                 {"type": "text", "text": "Delivery Note Number"},
            #                 {"type": "text", "text": "LPO Number"},
            #                 {"type": "text", "text": "Driver Name"},
            #                 {"type": "text", "text": "Driver Contact"},
            #                 {"type": "text", "text": "Truck Number"},
            #                 {"type": "text", "text": "Tank Number"},
            #                 {"type": "text", "text": "Point of Origin"},
            #                 {"type": "text", "text": "Final Destination"},
            #                 {"type": "text", "text": "Port of Discharge"},
            #                 {"type": "text", "text": "Country of Final Destination"},
            #                 {"type": "text", "text": "1st Weight"},
            #                 {"type": "text", "text": "2nd Weight"},
            #                 {"type": "text", "text": "Net Weight"},
            #                 {"type": "text", "text": "OCR Seals"},
            #                 {"type": "text", "text": "For PRODUCTS: Extract ALL products listed, including for each:\n"
            #                                          "  - Product Name\n"
            #                                          "  - Quantity\n"
            #                                          "  - Unit Price\n"
            #                                          "  - Total Price\n"
            #                                          "  - Batch Number\n"
            #                                          "  - LPO Number"},
            #                 {"type": "text", "text": "Return the response exactly in this format:"},
            #                 {"type": "text", "text": '''
            # {
            #   "Delivery Note Number": "48476",
            #   "LPO Number/Customer PO": "24005113/R1",
            #   "Invoice Number": null,
            #   "Driver Name": "SAMMY . K. KANGOGO",
            #   "Driver Contact": "0717-314456",
            #   "Truck Number": "KBD 307Q / ZD 6252",
            #   "Tank Number": null,
            #   "Point of Origin": null,
            #   "Final Destination": "Pwani Oil Products Limited, Mombasa",
            #   "Port of Discharge": null,
            #   "Country of Final Destination": "Kenya",
            #   "1st Weight": null,
            #   "2nd Weight": null,
            #   "Net Weight": null,
            #   "OCR Seals": "069192",
            #   "Product Items": [
            #     {
            #       "Serial Number": 1,
            #       "Product Name": "Round Jerrycan Yellow 20ltr 800gms",
            #       "Quantity": "2,178 ea",
            #       "Unit Price": null,
            #       "Total Price": null,
            #       "Batch Number": "FG40000164",
            #       "LPO Number": null
            #     },
            #     {
            #       "Serial Number": 2,
            #       "Product Name": "Bung Cap & Gasket Sky Blue 10/20ltr",
            #       "Quantity": "2,178 ea",
            #       "Unit Price": null,
            #       "Total Price": null,
            #       "Batch Number": "FG41000286",
            #       "LPO Number": null
            #     },
            #     {
            #       "Serial Number": 3,
            #       "Product Name": "Woven Bags for 20ltr 95 x 135",
            #       "Quantity": "363 ea",
            #       "Unit Price": null,
            #       "Total Price": null,
            #       "Batch Number": "PG20000134",
            #       "LPO Number": null
            #     }
            #   ]
            # }
            #                 '''},
            #                 {
            #                     "type": "image_url",
            #                     "image_url": {
            #                         "url": f"data:image/jpeg;base64,{image_base64}"
            #                     }
            #                 }
            #             ]
            #         }
            #     ],
            #     max_tokens=10000,
            #     temperature=0
            # )

            ############################
            response = client.chat.completions.create(
            model='o4-mini-2025-04-16',
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an information extraction assistant. Extract the requested fields from the delivery note image "
                        "and return the output ONLY in the exact following JSON structure. Do not add any commentary or explanation. "
                        "All keys must be present, even if values are 'Not provided.' or 'Not explicitly listed.'."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the following details from the delivery note image."},
                        {"type": "text", "text": "Required fields:"},
                        {"type": "text", "text": "1st weight"},
                        {"type": "text", "text": "2nd weight"},
                        {"type": "text", "text": "Back Plate Number"},
                        {"type": "text", "text": "Front Plate Number"},
                        {"type": "text", "text": "Net weight"},
                        {"type": "text", "text": "countryOfFinalDestination"},
                        {"type": "text", "text": "deliveryNoteNumber"},
                        {"type": "text", "text": "driverContact"},
                        {"type": "text", "text": "driverName"},
                        {"type": "text", "text": "finalDestination"},
                        {"type": "text", "text": "lpoNumber"},
                        {"type": "text", "text": "ocrSeals"},
                        {"type": "text", "text": "pointOfOrigin"},
                        {"type": "text", "text": "portOfDischarge"},
                        {"type": "text", "text": "tankNumber"},
                        {"type": "text", "text": "truck_Number"},
                        {"type": "text", "text": "products (include serialNumber, productName, quantity, unitPrice, totalPrice, batchNumber, lpoNumber)"},
                        {"type": "text", "text": "Return the response exactly in this JSON format:"},
                        {"type": "text", "text": '''
                        {
                            "1st weight": "Not provided.",
                            "2nd weight": "Not provided.",
                            "Back Plate Number": "0",
                            "Front Plate Number": "KDD158L",
                            "Net weight": "Not provided.",
                            "countryOfFinalDestination": "Kenya",
                            "deliveryNoteNumber": "BPD/DN070720/2024",
                            "driverContact": "0743256147",
                            "driverName": "JACKSON THOYA",
                            "finalDestination": "Not explicitly listed.",
                            "lpoNumber": "Not explicitly listed.",
                            "ocrSeals": [
                                "Not legible on the document."
                            ],
                            "pointOfOrigin": "Not explicitly listed.",
                            "portOfDischarge": "Not explicitly listed.",
                            "products": [
                                {
                                    "serialNumber": 1,
                                    "productName": "20LTR ROUND 800MLS LW PLAIN JCAR.DN",
                                    "quantity": "1,544",
                                    "unitPrice": "Not explicitly listed.",
                                    "totalPrice": "Not explicitly listed.",
                                    "batchNumber": "61207312",
                                    "lpoNumber": "Not explicitly listed."
                                },
                                {
                                    "serialNumber": 2,
                                    "productName": "20LTR BUNG CAP BLUE WITH RING",
                                    "quantity": "1,544",
                                    "unitPrice": "Not explicitly listed.",
                                    "totalPrice": "3,088.00",
                                    "batchNumber": "211010R-BLU",
                                    "lpoNumber": "Not explicitly listed."
                                }
                            ],
                            "tankNumber": "Not explicitly listed.",
                            "truck_Number": "KDD158L"
                        }
                        '''},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            
        )

            ###########################

        #     response = client.chat.completions.create(
        #     model='gpt-4o',
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": (
        #                 "You are an information extraction assistant. Extract the requested fields from the delivery note image "
        #                 "and return the output ONLY in the exact following JSON structure. Do not add any commentary or explanation. "
        #                 "All keys must be present, even if values are 'Not provided.' or 'Not explicitly listed.'."
        #             )
        #         },
        #         {
        #             "role": "user",
        #             "content": [
        #                 {"type": "text", "text": "Extract the following details from the delivery note image."},
        #                 {"type": "text", "text": "Required fields:"},
        #                 {"type": "text", "text": "1st weight"},
        #                 {"type": "text", "text": "2nd weight"},
        #                 {"type": "text", "text": "Back Plate Number"},
        #                 {"type": "text", "text": "Front Plate Number"},
        #                 {"type": "text", "text": "Net weight"},
        #                 {"type": "text", "text": "countryOfFinalDestination"},
        #                 {"type": "text", "text": "deliveryNoteNumber"},
        #                 {"type": "text", "text": "driverContact"},
        #                 {"type": "text", "text": "driverName"},
        #                 {"type": "text", "text": "finalDestination"},
        #                 {"type": "text", "text": "lpoNumber"},
        #                 {"type": "text", "text": "ocrSeals"},
        #                 {"type": "text", "text": "pointOfOrigin"},
        #                 {"type": "text", "text": "portOfDischarge"},
        #                 {"type": "text", "text": "tankNumber"},
        #                 {"type": "text", "text": "truck_Number"},
        #                 {"type": "text", "text": "products (include serialNumber, productName, quantity, unitPrice, totalPrice, batchNumber, lpoNumber)"},
        #                 {"type": "text", "text": "Return the response exactly in this JSON format:"},
        #                 {"type": "text", "text": ''' always include ```json in the output
        # {
          
        #     "1st weight": "Not provided.",
        #     "2nd weight": "Not provided.",
        #     "Back Plate Number": "0",
        #     "Front Plate Number": "KDD158L",
        #     "Net weight": "Not provided.",
        #     "countryOfFinalDestination": "Kenya",
        #     "deliveryNoteNumber": "BPD/DN070720/2024",
        #     "driverContact": "0743256147",
        #     "driverName": "JACKSON THOYA",
        #     "finalDestination": "Not explicitly listed.",
        #     "lpoNumber": "Not explicitly listed.",
        #     "ocrSeals": [
        #       "Not legible on the document."
        #     ],
        #     "pointOfOrigin": "Not explicitly listed.",
        #     "portOfDischarge": "Not explicitly listed.",
        #     "products": [
        #       {
        #         "serialNumber": 1,
        #         "productName": "20LTR ROUND 800MLS LW PLAIN JCAR.DN",
        #         "quantity": "1,544",
        #         "unitPrice": "Not explicitly listed.",
        #         "totalPrice": "Not explicitly listed.",
        #         "batchNumber": "61207312",
        #         "lpoNumber": "Not explicitly listed."
        #       },
        #       {
        #         "serialNumber": 2,
        #         "productName": "20LTR BUNG CAP BLUE WITH RING",
        #         "quantity": "1,544",
        #         "unitPrice": "Not explicitly listed.",
        #         "totalPrice": "3,088.00",
        #         "batchNumber": "211010R-BLU",
        #         "lpoNumber": "Not explicitly listed."
        #       }
        #     ],
        #     "tankNumber": "Not explicitly listed.",
        #     "truck_Number": "KDD158L"
        #   }
        # }
        #                 '''},
        #                 {
        #                     "type": "image_url",
        #                     "image_url": {
        #                         "url": f"data:image/jpeg;base64,{image_base64}"
        #                     }
        #                 }
        #             ]
        #         }
        #     ],
        #     max_tokens=5000,
        #     temperature=0
        # )

            # response = client.chat.completions.create(
            #     model='gpt-4o',
            #     messages=[
            #     {
            #         "role": "user",
            #         "content": [
            #             {"type": "text", "text": "Extract the following details from the delivery note:"},
            #             {"type": "text", "text": "Delivery Note Number"},
            #             {"type": "text", "text": "LPO Number"},
            #             {"type": "text", "text": "Driver Name"},
            #             {"type": "text", "text": "Driver Contact"},
            #             {"type": "text", "text": "Truck Number"},
            #             {"type": "text", "text": "Tank Number"},
            #             {"type": "text", "text": "Point of Origin"},
            #             {"type": "text", "text": "Final Destination"},
            #             {"type": "text", "text": "Port of Discharge"},
            #             {"type": "text", "text": "Country of Final Destination"},
            #             {"type": "text", "text": "1st Weight"},
            #             {"type": "text", "text": "2nd Weight"},
            #             {"type": "text", "text": "Net Weight"},
            #             {"type": "text", "text": "Products(Name, Quantity, Unit Price, Total Price, Batch Number, LPO Number)"},
            #             {"type": "text", "text": "OCR Seals"},
            #             {
            #                 "type": "image_url",
            #                 "image_url": {
            #                     "url": f"data:image/jpeg;base64,{image_base64}"
            #                 }
            #             }
            #         ]
            #     }
            # ],
            #     max_tokens=5000,
            # )

            if not response or not response.choices or not response.choices[0].message.content:
                return "Error: No content returned"

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"

    def convert_pdf_to_image(self, pdf_path):
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        image_path = "temp_page.jpg"
        images[0].save(image_path, "JPEG")
        return image_path
    
def save_as_json(content, filename):
    json_filename = f"{filename}.json"
    parsed_content = {"content": content}
    with open(json_filename, 'w') as json_file:
        json.dump(parsed_content, json_file, indent=4)

def save_as_pdf(content, filename):
    pdf_filename = f"{filename}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = content.split("\n")
    for line in lines:
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(pdf_filename)

def process_delivery_note_image(file_path):
        extractor = DeliveryNoteTextExtractor(api_key=os.environ["OPENAI_API_KEY"])
        content = extractor.extract_text(file_path)

        if "Error" not in content:
            base_filename = os.path.splitext(os.path.basename(file_path))[0]
            save_as_json(content, base_filename)
            save_as_pdf(content, base_filename)
        
            return content
        else:
            return None

