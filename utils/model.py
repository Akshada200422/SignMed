import cv2
import numpy as np
import logging

# ---------------- LOAD MODEL ----------------
try:
    from cvzone.HandTrackingModule import HandDetector
    from cvzone.ClassificationModule import Classifier

    classifier = Classifier(
        "Models/EmergencyModel/keras_model.h5",
        "Models/EmergencyModel/labels.txt"
    )
    detector = HandDetector(maxHands=2)
    MODEL_LOADED = True
    logging.info("✅ Model and detector loaded successfully.")
except Exception as e:
    logging.error(f"❌ Model load failed: {e}")
    MODEL_LOADED = False
    detector = None
    classifier = None

labels = ["Breathless", "Cold", "Cough", "Help", "Vomit"]

sentences = {
    "Breathless": "I am feeling breathless.",
    "Cold":       "I am feeling cold.",
    "Cough":      "I am not feeling well because I have a cough.",
    "Help":       "I need help.",
    "Vomit":      "I feel like vomiting."
}

offset  = 20
imgSize = 300

# ── Global state (updated by generate_frames loop) ──
latest_label    = "No Detection"
latest_sentence = ""
latest_accuracy = ""

# ── Singleton camera — opened once, shared everywhere ──
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    logging.warning("CAP_DSHOW failed, trying default backend...")
    cap = cv2.VideoCapture(0)

# Shared latest JPEG frame for the /video route
latest_frame = None


def generate_frames():
    """
    Main loop — reads camera, runs detection, updates globals.
    Also yields MJPEG frames for the /video route.
    Calling this a second time (from /video) just reads latest_frame.
    """
    global latest_label, latest_sentence, latest_accuracy, latest_frame

    while True:
        success, img = cap.read()
        if not success:
            logging.warning("Camera read failed — retrying...")
            continue

        imgOutput = img.copy()

        label    = "No Detection"
        sentence = ""
        accuracy = ""

        if detector is not None:
            try:
                hands, img_with_hands = detector.findHands(img)
            except Exception as e:
                logging.error(f"Hand detection error: {e}")
                hands = []

            if hands:
                height, width, _ = img.shape

                if len(hands) >= 2:
                    x1, y1, w1, h1 = hands[0]['bbox']
                    x2, y2, w2, h2 = hands[1]['bbox']
                    x_min = max(0, min(x1, x2) - offset)
                    y_min = max(0, min(y1, y2) - offset)
                    x_max = min(width,  max(x1+w1, x2+w2) + offset)
                    y_max = min(height, max(y1+h1, y2+h2) + offset)
                else:
                    x, y, w, h = hands[0]['bbox']
                    x_min = max(0, x - offset)
                    y_min = max(0, y - offset)
                    x_max = min(width,  x + w + offset)
                    y_max = min(height, y + h + offset)

                if x_max > x_min and y_max > y_min:
                    imgCrop  = img[y_min:y_max, x_min:x_max]
                    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

                    cropH, cropW = imgCrop.shape[:2]
                    if cropH == 0 or cropW == 0:
                        pass
                    else:
                        aspectRatio = cropH / cropW
                        if aspectRatio > 1:
                            scale   = imgSize / cropH
                            newW    = int(cropW * scale)
                            resized = cv2.resize(imgCrop, (newW, imgSize))
                            wGap    = (imgSize - newW) // 2
                            imgWhite[:, wGap:wGap+newW] = resized
                        else:
                            scale   = imgSize / cropW
                            newH    = int(cropH * scale)
                            resized = cv2.resize(imgCrop, (imgSize, newH))
                            hGap    = (imgSize - newH) // 2
                            imgWhite[hGap:hGap+newH, :] = resized

                        if MODEL_LOADED:
                            try:
                                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                                confidence        = prediction[index]
                                predicted_label   = labels[index]

                                if confidence > 0.60:
                                    label    = predicted_label
                                    sentence = sentences.get(label, "")
                                else:
                                    label    = "Uncertain"
                                    sentence = ""

                                accuracy = f"{confidence * 100:.2f}%"
                                logging.debug(f"Prediction: {label} @ {accuracy}")
                            except Exception as e:
                                logging.error(f"Classifier error: {e}")
                                label = "Error"

                    # Draw bounding box on output
                    cv2.rectangle(imgOutput,
                                  (x_min, y_min), (x_max, y_max),
                                  (255, 0, 255), 3)
                    cv2.putText(imgOutput,
                                f"{label} ({accuracy})",
                                (x_min, max(y_min - 10, 20)),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8,
                                (0, 255, 0), 2)

        # Update globals
        latest_label    = label
        latest_sentence = sentence
        latest_accuracy = accuracy

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', imgOutput)
        if not ret:
            continue

        frame = buffer.tobytes()
        latest_frame = frame  # store for /video route

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
