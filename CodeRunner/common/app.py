#######################
# Add your imports here
#######################
import cv2
import numpy as np
import base64

############################
# Enter you Bucket name here
############################
BUCKET_NAME = ""


def read_base64_image(base64_string):
    # Decode the base64 string into bytes
    image_bytes = base64.b64decode(base64_string)

    # Convert the bytes into a NumPy array
    np_arr = np.frombuffer(image_bytes, np.uint8)

    # Decode the array into an image
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return image


def encode_base64_image(image):
    # Convert the image to JPEG format
    _, jpeg_image = cv2.imencode(".jpg", image)

    # Convert the JPEG image to base64 string
    base64_string = base64.b64encode(jpeg_image).decode()

    return base64_string


def userDefinedFunction(image_old):  # This is a Base664 encoded string
    image_new = ""
    # Read the base64 image
    image_old = read_base64_image(image_old)
    # Apply blur effect
    blurred_image = cv2.GaussianBlur(image_old, (15, 15), 0)
    image_new = encode_base64_image(blurred_image)
    return image_new
