#######################
# Add your imports here
from PIL import Image, ImageOps
import base64
import io
import time
#######################
############################
# Enter you Bucket name here
############################
BUCKET_NAME = "myfnone"


def read_base64_image(base64_string):
    image_data = base64.b64decode(base64_string)
    image_stream = io.BytesIO(image_data)

    return image_stream


def encode_base64_image(image):
    image_stream = io.BytesIO()
    image.save(image_stream, format="PNG")
    _image_bytes = image_stream.getvalue()
    base64_string = base64.b64encode(_image_bytes).decode("utf-8")
    return base64_string


def userDefinedFunction(image_old):
    image_new = "BLANK"
    start_time = time.time()
    with Image.open(read_base64_image(image_old)) as im:
        im = ImageOps.grayscale(im)
        encoded = encode_base64_image(im)
        end_time = time.time()
        print("Time:", end_time - start_time)
        image_new= encoded
        return image_new
