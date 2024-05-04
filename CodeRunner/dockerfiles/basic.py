import numpy as np
import time


def userDefinedFunction(image_old):
    start_time = time.time()
    matrix1 = np.random.rand(2000, 2000)
    matrix2 = np.random.rand(2000, 2000)
    result = np.dot(matrix1, matrix2)
    end_time = time.time()
    print("Time:", end_time - start_time)
    return image_old
