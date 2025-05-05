import openai
import os
import shutil
import base64
from ultralytics import YOLO
from PIL import Image
import streamlit as st
from openai import OpenAI
# Initialize the YOLO model
model_path = r"C:\Users\User\OneDrive - ALGO8 AI PRIVATE LIMITED\pwani_module-Shraddha\license_plate_detector.pt"  # Replace with your YOLO .pt file path
model = YOLO(model_path)
os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI()

# Temporary folders for processing
temp_input_folder = r"temp_input"
temp_output_folder = r"temp_output"
temp_cropped_folder = r"temp_cropped"

# Ensure directories exist
os.makedirs(temp_input_folder, exist_ok=True)
os.makedirs(temp_output_folder, exist_ok=True)
os.makedirs(temp_cropped_folder, exist_ok=True)

# Function to clear temporary folders
def clear_temp_folders():
    for folder in [temp_input_folder, temp_output_folder, temp_cropped_folder]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

# Function to process the uploaded image and detect the license plate
def process_image(image_path):
    # Run inference with YOLO
    results = model.predict(source=image_path, save=True, save_crop=True)
    cropped_image_path = None

    # Process results and save the cropped license plate
    for result in results:
        result_dir = result.save_dir  # Directory where YOLO saves results
        for item in os.listdir(result_dir):
            src_path = os.path.join(result_dir, item)
            if "crops" in item.lower():  # Look for cropped images
                crop_dir = src_path
                for sub_folder in os.listdir(crop_dir):
                    sub_folder_path = os.path.join(crop_dir, sub_folder)
                    for crop_item in os.listdir(sub_folder_path):
                        src_crop_path = os.path.join(sub_folder_path, crop_item)
                        cropped_image_path = os.path.join(temp_cropped_folder, crop_item)
                        shutil.copy(src_crop_path, cropped_image_path)
    return cropped_image_path

# Function to extract text from the cropped license plate image using GPT-4

def extract_text(image_path):
    # Convert the image to Base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Make a call to OpenAI's API for text extraction
    response = client.chat.completions.create(
        model='gpt-4o',
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "take out the alphabets and number with special character from the license plate in the image. Use this JSON Schema: " },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500,
    ) 
    print(response.choices[0].message.content)
    extracted_text = response.choices[0].message.content
    return extracted_text

# Streamlit app interface
st.title("Automatic Number Plate Recognition (ANPR)")

# Upload image
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image:
    # Clear previous temporary files
    clear_temp_folders()

    # Save the uploaded image to a temporary file
    input_image_path = os.path.join(temp_input_folder, uploaded_image.name)
    with open(input_image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())

    # Display the uploaded image
    st.image(input_image_path, caption="Uploaded Image", use_column_width=True)

    # Process the image to detect and crop the license plate
    st.write("Processing the image...")
    cropped_image_path = process_image(input_image_path)

    if cropped_image_path:
        # Display the cropped license plate
        st.image(cropped_image_path, caption="Cropped License Plate", use_column_width=True)

        # Extract text from the cropped license plate
        st.write("Extracting text from the license plate...")
        extracted_text = extract_text(cropped_image_path)
        print(extracted_text)
        if extracted_text:
            st.write(f"**Extracted Text:** {extracted_text}")
        else:
            st.error("Error extracting text from the license plate.")
    else:
        st.error("No license plate detected in the image.")

# Clean up temporary files manually
if st.button("Clear Temporary Files"):
    clear_temp_folders()
    st.success("Temporary files cleared!")
