import cv2
import matplotlib.pyplot as plt
import time


def apply_histogram_equalization(image_path):
    """
    Applies histogram equalization to an image.

    Args:
        image_path (str): Path to the input image file.

    Returns:
        numpy.ndarray: Image with improved contrast.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    equalized_image = cv2.equalizeHist(image)
    return equalized_image


# Example usage
input_image_path = "IMG_6501.png"
start_time = time.time()
equalized_result = apply_histogram_equalization(input_image_path)
end_time = time.time()
print("Time:", end_time - start_time)
plt.imshow(equalized_result)
plt.axis("off")
plt.show()
