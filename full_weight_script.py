import os
from anpr_app import LicensePlateDetector, TextExtractor
from format_conv import extract_details
from ultralytics import YOLO

model_path = r"license_plate_detector.pt"
model = YOLO(model_path)

license_plate_detector = LicensePlateDetector(
    model_path = r"license_plate_detector.pt",
    temp_input="input_folder",
    temp_output="output_folder",
    temp_cropped="cropped_folder"
)

def process_request(data):
    
    if not data:
        raise ValueError("No data provided in the request")
    
    
    truck_image_path = data.get('truck_image_path')

    if  not truck_image_path:
        raise ValueError("Missing truck_image_path in payload")

    # Extract truck number from the truck image
    cropped_image_path = license_plate_detector.process_image(truck_image_path)
    license_plate_text = ""

    if cropped_image_path:
        license_plate_text = TextExtractor.extract_text(cropped_image_path)
    else:
        raise ValueError("No license plate detected in the truck image")



    # Compare the truck numbers
    result = {
        'license_plate_text': license_plate_text,
        'Full Weight Sensor' : "42561"
    }

    # Add cropped truck number plate image path if detected
    if cropped_image_path and os.path.exists(cropped_image_path):
        result['cropped_image_path'] = cropped_image_path

    return result
