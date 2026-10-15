# SignMed — Sign Language Emergency Translator

Real-time sign language to text translation for emergency medical care.

---

## Project Structure

```
SignMed/
├── app.py                   ← Flask server (entry point)
├── dataCollection.py        ← Collect training images
├── requirements.txt
├── templates/
│   ├── home.html            ← Landing page
│   └── test.html            ← Live translator page
├── static/
│   ├── css/
│   │   ├── style.css        ← Shared styles
│   │   └── test.css         ← Translator page styles
│   └── JS/
│       ├── home.js
│       └── test.js
├── utils/
│   ├── __init__.py
│   └── model.py             ← Camera + ML model logic
└── Models/
    └── EmergencyModel/
        ├── keras_model.h5   ← ⬅ PUT YOUR TRAINED MODEL HERE
        └── labels.txt       ← ⬅ PUT YOUR LABELS FILE HERE
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your model files

Copy your trained model files into:

```
Models/EmergencyModel/keras_model.h5
Models/EmergencyModel/labels.txt
```

### 3. Run the server

```bash
python app.py
```

### 4. Open in browser

```
http://localhost:5000
```

---

## Routes

| Route             | Description                     |
| ----------------- | ------------------------------- |
| `/`               | Home / landing page             |
| `/home`           | Home / landing page             |
| `/test`           | Live translator UI              |
| `/video`          | MJPEG video stream              |
| `/get_prediction` | JSON: label, sentence, accuracy |

---

## Supported Signs

| Sign       | Sentence Output                                 |
| ---------- | ----------------------------------------------- |
| Breathless | "I am feeling breathless."                      |
| Cold       | "I am feeling cold."                            |
| Cough      | "I am not feeling well because I have a cough." |
| Help       | "I need help."                                  |
| Vomit      | "I feel like vomiting."                         |

---

## Data Collection

To collect new training images, run:

```bash
python dataCollection.py
```

- Change the `folder` variable at the top to the word you're collecting.
- Show **both hands** in frame.
- Press **S** to save an image.
- Press **Q** to quit.

---

## Notes

- Confidence threshold is set to **80%** in `utils/model.py`. Lower it if detection is too strict.
- Model supports **2 hands** (matching how data was collected).
- The `/get_prediction` endpoint is polled every **500ms** by the frontend.
