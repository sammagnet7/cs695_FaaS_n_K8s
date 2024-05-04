import cv2
import matplotlib.pyplot as plt
import time


def apply_canny_edge_detection(image_path, low_threshold=50, high_threshold=150):
    """
    Applies Canny edge detection to an image.

    Args:
        image_path (str): Path to the input image file.
        low_threshold (int): Lower threshold for edge detection.
        high_threshold (int): Higher threshold for edge detection.

    Returns:
        numpy.ndarray: Image with detected edges.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, low_threshold, high_threshold)
    return edges


# Example usage
input_image_path = "IMG8K3.jpg"
start_time = time.time()
edges_result = apply_canny_edge_detection(input_image_path, 50, 100)
end_time = time.time()
print("Time:", end_time - start_time)
plt.imshow(edges_result)
plt.axis("off")
plt.show()
