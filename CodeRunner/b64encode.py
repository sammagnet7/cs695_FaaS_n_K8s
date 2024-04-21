import base64

# Define the string you want to encode
string_to_encode = "hello"


# Encode the string to Base64
def encode(string):
    encoded_bytes = base64.b64encode(string_to_encode.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


# Print the Base64 encoded string
print(encode(string_to_encode))
