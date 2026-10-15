from flask import Flask, render_template, Response, jsonify
import logging
import threading

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
logging.basicConfig(level=logging.DEBUG)

# ── Start the camera/model loop in a background thread on startup ──
def start_model():
    try:
        from utils.model import generate_frames
        logging.info("Model thread started — consuming frames...")
        for _ in generate_frames():
            pass  # keep the generator running so globals stay updated
    except Exception as e:
        logging.error(f"Model thread crashed: {e}")

model_thread = threading.Thread(target=start_model, daemon=True)
model_thread.start()
logging.info("Background model thread launched.")

# ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/video")
def video():
    try:
        from utils.model import generate_frames
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logging.error(f"Video route error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_prediction")
def get_prediction():
    try:
        import utils.model as m
        return jsonify({
            "label":    m.latest_label,
            "sentence": m.latest_sentence,
            "accuracy": m.latest_accuracy
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
