import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time
import os

# Webcam
cap = cv2.VideoCapture(0)

# Detect up to 2 hands
detector = HandDetector(maxHands=2)

offset  = 20
imgSize = 300

# ✅ Change this to the word you are collecting
folder  = "EmergencyWords/Help/"
counter = 0

os.makedirs(folder, exist_ok=True)

while True:
    success, img = cap.read()
    if not success:
        continue

    imgOutput = img.copy()
    hands, img = detector.findHands(img)

    if len(hands) == 2:
        x1, y1, w1, h1 = hands[0]['bbox']
        x2, y2, w2, h2 = hands[1]['bbox']

        height, width, _ = img.shape

        x_min = max(0, min(x1, x2) - offset)
        y_min = max(0, min(y1, y2) - offset)
        x_max = min(width,  max(x1+w1, x2+w2) + offset)
        y_max = min(height, max(y1+h1, y2+h2) + offset)

        imgCrop  = img[y_min:y_max, x_min:x_max]
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

        cropH, cropW = imgCrop.shape[:2]
        aspectRatio  = cropH / cropW

        if aspectRatio > 1:
            scale  = imgSize / cropH
            newW   = int(cropW * scale)
            resized = cv2.resize(imgCrop, (newW, imgSize))
            wGap   = (imgSize - newW) // 2
            imgWhite[:, wGap:wGap+newW] = resized
        else:
            scale  = imgSize / cropW
            newH   = int(cropH * scale)
            resized = cv2.resize(imgCrop, (imgSize, newH))
            hGap   = (imgSize - newH) // 2
            imgWhite[hGap:hGap+newH, :] = resized

        cv2.imshow("ImageCrop",  imgCrop)
        cv2.imshow("ImageWhite", imgWhite)

        key = cv2.waitKey(1)
        if key == ord("s"):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename  = f"{folder}/Image_{timestamp}_{counter}.jpg"
            cv2.imwrite(filename, imgWhite)
            counter += 1
            print(f"Saved: {filename} | Total: {counter}")

    elif len(hands) == 1:
        cv2.putText(imgOutput, "Show BOTH hands", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(imgOutput, "No hands detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Image", imgOutput)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
