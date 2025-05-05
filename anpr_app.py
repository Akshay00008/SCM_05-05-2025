import os
import shutil
import base64
from datetime import datetime
import numpy as np
import cv2
from ultralytics import YOLO
from openai import OpenAI

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI()

class LicensePlateDetector:
    def __init__(self, model_path, temp_input, temp_output, temp_cropped):
        self.model = YOLO(model_path)
        self.temp_input_folder = temp_input
        self.temp_output_folder = temp_output
        self.temp_cropped_folder = temp_cropped
        self._initialize_folders()

    def _initialize_folders(self):
        for folder in [self.temp_input_folder, self.temp_output_folder, self.temp_cropped_folder]:
            os.makedirs(folder, exist_ok=True)

    def clear_temp_folders(self):
        for folder in [self.temp_input_folder, self.temp_output_folder]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)

    def process_image(self, image_path):
        results = self.model.predict(source=image_path, save=True, save_crop=True)
        cropped_image_paths = []

        # Extract base name and timestamp
        original_name = os.path.splitext(os.path.basename(image_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        counter = 0  # To append a unique number to each cropped image filename

        # Process and save the cropped images
        for result in results:
            result_dir = result.save_dir
            for item in os.listdir(result_dir):
                src_path = os.path.join(result_dir, item)
                if "crops" in item.lower():
                    crop_dir = src_path
                    for sub_folder in os.listdir(crop_dir):
                        sub_folder_path = os.path.join(crop_dir, sub_folder)
                        for crop_item in os.listdir(sub_folder_path):
                            src_crop_path = os.path.join(sub_folder_path, crop_item)

                            # Generate unique filename
                            new_filename = f"{original_name}_{timestamp}_cropped_{counter}.jpg"
                            cropped_image_path = os.path.join(self.temp_cropped_folder, new_filename)

                            # Copy the cropped image to the target folder
                            shutil.copy(src_crop_path, cropped_image_path)

                            # Enhance and overwrite the image
                            self.enhance_image(cropped_image_path)
                            
                            # Append to list of cropped image paths
                            cropped_image_paths.append(cropped_image_path)
                            counter += 1

        return cropped_image_paths[0] if cropped_image_paths else None

    def enhance_image(self, image_path):
        """Enhances the cropped number plate image by applying Gaussian Blur and sharpening."""
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        cv2.imwrite(image_path, sharpened)


class TextExtractor:
    def extract_text(image_path):
        # Read the image and convert to base64
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

        # Create the OpenAI request payload
        response = client.chat.completions.create(
            model='o4-mini-2025-04-16',
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
  "text": "Extract the complete license plate number from the image, including all letters, numbers, and any special characters (e.g., dots, hyphens). Return the result using the following JSON schema:\n\n\"license_plate\":\\\"KBV·196A\\\"}\""
},
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

        extracted_text = response.choices[0].message.content
        return extracted_text

'''
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Paths
    model_path = r"license_plate_detector.pt"
    input_path = r"big_with_watermark_isuzu-elf-east-kenya-isiolo-16544.jpg"

    detector = LicensePlateDetector(model_path, "input_folder", "output_folder", "cropped_folder")
    text_extractor = TextExtractor(client)

    # Clear folders and process image
    detector.clear_temp_folders()
    cropped_image_path = detector.process_image(input_path)

    if cropped_image_path:
        extracted_text = text_extractor.extract_text(cropped_image_path)
        print(f"Extracted Text: {extracted_text}")

        # Show cropped and enhanced image
        cropped_image = cv2.imread(cropped_image_path)
        plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        plt.title(f"Extracted Text: {extracted_text}")
        plt.axis('off')
        plt.show()
'''