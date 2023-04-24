const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
const confirmPredictionButton = document.getElementById("confirm-prediction");
const clearPredictionButton = document.getElementById("clear-prediction");
const predictionDisplay = document.getElementById("prediction");
const confirmedPredictionsDisplay = document.getElementById("confirmed-predictions");

let confirmedPredictions = '';

navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then((stream) => {
  video.srcObject = stream;
});

function sendFrame() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL("image/jpeg", 0.8);

  fetch("/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "frame=" + encodeURIComponent(dataUrl),
  })
    .then((response) => response.json())
    .then((processedFrame) => {
      if (processedFrame.prediction) {
        predictionDisplay.textContent = processedFrame.prediction;
      } else {
        predictionDisplay.textContent = "";
      }
      const img = new Image();
      img.src = processedFrame.imgOutput;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(img, 0, 0, canvas.width, canvas.height);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

setInterval(sendFrame, 100);

confirmPredictionButton.addEventListener("click", () => {
  if (predictionDisplay.textContent) {
    confirmedPredictions += predictionDisplay.textContent;
    confirmedPredictionsDisplay.textContent = confirmedPredictions;
  }
});

clearPredictionButton.addEventListener("click", () => {
  confirmedPredictions = "";
  confirmedPredictionsDisplay.textContent = "";
});
