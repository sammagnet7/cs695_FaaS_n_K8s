from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import time


def multiply_images(image1, image2):
    """
    Multiply two image matrices.

    Args:
    - image1: numpy ndarray representing the first image matrix
    - image2: numpy ndarray representing the second image matrix

    Returns:
    - result: numpy ndarray representing the element-wise product of the two matrices
    """
    # Check if both matrices have the same shape
    if image1.shape != image2.shape:
        raise ValueError("Input matrices must have the same shape")

    # Multiply the matrices element-wise
    result = np.multiply(image1, image2)

    return result


img = Image.open("IMG8K.jpg")
np_img = np.array(img)
print(np_img.shape)
np_img = np_img / 255
start_time = time.time()
result = multiply_images(np_img, np_img)
end_time = time.time()
print("Time:", end_time - start_time)
plt.imshow(result)
plt.axis("off")
plt.show()
