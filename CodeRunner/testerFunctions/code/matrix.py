#######################
# Add your imports here
import numpy as np
import time
#######################
############################
# Enter you Bucket name here
############################
BUCKET_NAME = "yaml"

def userDefinedFunction(image_old):
    
    image_new = "BLANK"

    start_time = time.time()
    matrix1 = np.random.rand(2000, 2000)
    matrix2 = np.random.rand(2000, 2000)
    result = np.dot(matrix1, matrix2)
    end_time = time.time()
    #print("Time:", end_time - start_time)
    print("FINAL MATRIX VALUE: ", result)

    return image_new
