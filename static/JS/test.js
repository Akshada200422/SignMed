document.addEventListener("DOMContentLoaded", function () {
  const labelEl    = document.getElementById("label");
  const sentenceEl = document.getElementById("sentence");
  const accuracyEl = document.getElementById("accuracy");
  const barEl      = document.getElementById("accuracy-bar");
  const speakBtn   = document.getElementById("speak-btn");
  const clearBtn   = document.getElementById("clear-btn");

  let lastLabel = "";

  // Poll every 500ms
  setInterval(fetchPrediction, 500);
  fetchPrediction();

  function fetchPrediction() {
    fetch("/get_prediction")
      .then((res) => res.json())
      .then((data) => updateDisplay(data))
      .catch((err) => console.error("Prediction fetch error:", err));
  }

  function updateDisplay(data) {
    // --- Label ---
    const label = data.label || "Waiting...";
    if (label !== lastLabel) {
      labelEl.style.opacity = "0";
      setTimeout(() => {
        labelEl.textContent = label;
        labelEl.style.opacity = "1";
        labelEl.classList.toggle(
          "detected",
          label !== "Waiting..." && label !== "No Detection" && label !== "Uncertain" && label !== "No Hand"
        );
      }, 150);
      lastLabel = label;
    }

    // --- Sentence ---
    if (data.sentence && data.sentence.trim() !== "") {
      sentenceEl.innerHTML = `<p>${data.sentence}</p>`;
    } else {
      sentenceEl.innerHTML = `<p class="placeholder-text">Waiting for sign language input...</p>`;
    }

    // --- Accuracy ---
    // Backend sends string like "85.23%"
    const accStr = data.accuracy || "0%";
    const accNum = parseFloat(accStr); // parse "85.23%" → 85.23

    accuracyEl.textContent = isNaN(accNum) ? "0%" : accStr;
    barEl.style.width = (isNaN(accNum) ? 0 : Math.min(accNum, 100)) + "%";

    if (accNum < 50) {
      barEl.style.background = "linear-gradient(90deg, #ef4444, #f87171)";
    } else if (accNum < 75) {
      barEl.style.background = "linear-gradient(90deg, #f59e0b, #fbbf24)";
    } else {
      barEl.style.background = "linear-gradient(90deg, #10b981, #2563eb)";
    }
  }

  // Speak
  speakBtn.addEventListener("click", function () {
    const p = sentenceEl.querySelector("p");
    const text = p ? p.textContent.trim() : "";

    if (!text || text === "Waiting for sign language input...") {
      alert("No translation yet. Please perform a sign gesture.");
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang   = "en-US";
    utterance.rate   = 1;
    utterance.pitch  = 1;
    utterance.volume = 1;

    speakBtn.disabled = true;
    speakBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Speaking...</span>';

    utterance.onend = () => {
      speakBtn.disabled = false;
      speakBtn.innerHTML = '<i class="fas fa-volume-up"></i><span>Speak Aloud</span>';
    };

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  });

  // Clear
  clearBtn.addEventListener("click", function () {
    labelEl.textContent = "Waiting...";
    labelEl.classList.remove("detected");
    sentenceEl.innerHTML = `<p class="placeholder-text">Waiting for sign language input...</p>`;
    accuracyEl.textContent = "0%";
    barEl.style.width = "0%";
  });

  // Fade transitions for label
  labelEl.style.transition = "opacity 0.15s ease";
});
