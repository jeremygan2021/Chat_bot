#<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-Time Object Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        #video {
            border: 2px solid #333;
            width: 640px;
            height: 480px;
        }
        #results {
            margin-top: 20px;
            width: 640px;
            border: 2px solid #333;
            padding: 10px;
            background-color: #fff;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.11.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.0.4/dist/coco-ssd.min.js"></script>
</head>
<body>
    <div id="app">
        <video id="video" autoplay></video>
        <div id="results"></div>
    </div>
    <script>
        async function setup() {
            const model = await tf.loadGraphModel('model.json'); // Replace with the correct model loading method
            const video = document.getElementById('video');
            const resultsDiv = document.getElementById('results');
            let detectedObjects = new Set();
            let lastDetectionTime = Date.now();

            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
                video.srcObject = stream;
            } catch (error) {
                console.error('Error accessing screen recording:', error);
                return;
            }

            const detectObjects = () => {
                if (Date.now() - lastDetectionTime < 500) { // 2 FPS
                    requestAnimationFrame(detectObjects);
                    return;
                }
                lastDetectionTime = Date.now();

                model.detect(video).then(predictions => {
                    predictions.forEach(prediction => {
                        const classId = prediction.class;
                        if (!detectedObjects.has(classId)) {
                            detectedObjects.add(classId);
                            resultsDiv.innerHTML += `<p>${classId} detected at ${new Date().toLocaleTimeString()}</p>`;
                        }
                        drawBoundingBox(prediction);
                    });
                });

                requestAnimationFrame(detectObjects);
            };

            detectObjects();

            function drawBoundingBox(prediction) {
                const videoCtx = video.getContext('2d');
                const [x, y, width, height] = prediction.bbox;
                videoCtx.strokeStyle = 'red';
                videoCtx.strokeRect(x, y, width, height);
                videoCtx.fillText(`${prediction.class}: ${prediction.score.toFixed(2)}`, x, y - 5);
            }
        }

        setup().catch(error => console.error('Error setting up:', error));
    </script>
</body>
</html>
