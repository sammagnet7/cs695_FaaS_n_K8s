import cv2
import matplotlib.pyplot as plt
import time

start_time = time.time()

imagePath = (
    "/home/arif/Kube/cs695/FAAS/cs695_FaaS_n_K8s/CodeRunner/uploads/common/IMG_6501.png"
)
img = cv2.imread(imagePath)


def detectFaces(img):
    img_rgb = ""
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    face = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.07, minNeighbors=3, minSize=(2, 2)
    )
    for x, y, w, h in face:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb


detectFaces(img)
execution_time = time.time() - start_time
print("Execution time in seconds: " + str(execution_time))
