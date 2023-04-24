import base64
import cv2
import numpy as np
import math
from flask import Flask, render_template, Response, request, jsonify
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
from flask_cors import CORS


from io import BytesIO

from cvzone.ClassificationModule import Classifier

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

offset = 20
imgSize = 300
labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
          "W", "X", "Y", "Z"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    frame_data = request.form.get('frame')
    frame_data = frame_data.split(',')[1]
    frame_data = base64.b64decode(frame_data)
    frame_data = np.frombuffer(frame_data, dtype=np.uint8)
    img = cv2.imdecode(frame_data, flags=1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    imgOutput = img.copy()
    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = img[y-offset:y+h+offset, x-offset:x+w+offset]

        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize - wCal) / 2)

            imgWhite[:, wGap:wCal+wGap] = imgResize
            prediction, index = classifier.getPrediction(imgWhite, draw=False)

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap:hCal + hGap, :] = imgResize
            prediction, index = classifier.getPrediction(imgWhite, draw=False)

        cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50), (255, 0, 255), cv2.FILLED)
        cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)

    _, imgOutput = cv2.imencode('.jpg', cv2.cvtColor(imgOutput, cv2.COLOR_RGB2BGR))

    imgOutput = base64.b64encode(imgOutput.tobytes()).decode('utf-8')

    response = {
        'prediction': labels[index] if hands else None,
        'imgOutput': 'data:image/jpeg;base64,' + imgOutput,
        'bbox': hand['bbox'] if hands else None
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
