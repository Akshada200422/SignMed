# test_model.py
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import os

print("=== CHECKING MODEL FILES ===")
print("keras_model.h5 exists:", os.path.exists("Models/EmergencyModel/keras_model.h5"))
print("labels.txt exists:", os.path.exists("Models/EmergencyModel/labels.txt"))

print("\n=== LOADING MODEL ===")
try:
    classifier = Classifier("Models/EmergencyModel/keras_model.h5", "Models/EmergencyModel/labels.txt")
    print("Model loaded successfully!")
except Exception as e:
    print("Model load ERROR:", e)

print("\n=== TESTING CAMERA ===")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Camera open:", cap.isOpened())

detector = HandDetector(maxHands=2)

print("\n=== STARTING DETECTION (press Q to quit) ===")
while True:
    success, img = cap.read()
    if not success:
        print("Camera read failed!")
        break

    hands, img = detector.findHands(img)
    print(f"Hands detected: {len(hands)}", end="\r")

    if len(hands) > 0:
        print(f"\nHand found! Confidence test...")
        break

    cv2.imshow("Test", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()