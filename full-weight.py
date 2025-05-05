from anpr_app import LicensePlateDetector, TextExtractor
from delivery_note import DeliveryNoteTextExtractor
from format_conv import extract_details
import cv2
import matplotlib.pyplot as plt

img = r"C:\Users\User\OneDrive - ALGO8 AI PRIVATE LIMITED\pwani-scm\big_with_watermark_isuzu-elf-east-kenya-isiolo-16544.jpg"

license_plate = LicensePlateDetector( 
    temp_input=r"input_folder", 
    temp_output=r"output_folder", 
    temp_cropped=r"cropped_folder"
)
license_plate_text=""

cropped_image_path = license_plate.process_image(img)

if cropped_image_path:
    cropped_image = cv2.imread(cropped_image_path)
    license_plate_text= TextExtractor.extract_text(cropped_image_path)
    print(license_plate_text)
    plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    plt.title(license_plate_text)
    plt.axis('off')
    plt.show()
    
else:
    print("No license plate detected in the image.")
    
print("i found license plate text is", license_plate_text)
dn_img=r"C:\Users\User\OneDrive - ALGO8 AI PRIVATE LIMITED\pwani-scm\Screenshot (683).png"
dn=DeliveryNoteTextExtractor.extract_text(dn_img,dn_img)
dn_data= extract_details(dn)
#print(dn_data)
#print(type(dn_data))
dn_truck_number = dn_data.get('truck_Number', 'Key not found')
print(dn_truck_number)

if (license_plate_text==dn_truck_number):
    print("matched")
print("no match")
