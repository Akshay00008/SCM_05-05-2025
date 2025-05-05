from openai import OpenAI
import os
import shutil
import base64

os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI()

def _initialize_folders(self):
        for folder in [self.temp_input_folder, self.temp_output_folder, self.temp_cropped_folder]:
            os.makedirs(folder, exist_ok=True)

def clear_temp_folders(self):
        for folder in [self.temp_input_folder, self.temp_output_folder, self.temp_cropped_folder]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)

class NumberExtractor:
    

    def extract_text(self,image_path):
        # Read the image and convert to base64
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Create the OpenAI request payload
        response = client.chat.completions.create(
            model='gpt-4-turbo',
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """take out the alphabets and number with special character in the image response should be in this form  ["{"number": "844652"}"]. Use this JSON Schema: """},
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

        extracted_text = response.choices[0].message.content
        return extracted_text

