const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 8000;

// Enable CORS for React frontend
app.use(cors());
app.use(express.json());

// Model info endpoint
app.get('/model-info', (req, res) => {
    res.json({
        model_name: "YOLOv8",
        version: "8.0.0",
        input_size: [640, 640],
        classes: [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
            "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
            "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
            "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
            "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
            "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
            "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
            "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
            "toothbrush"
        ],
        status: "ready"
    });
});

// Detection endpoint
app.post('/detect', (req, res) => {
    try {
        // Mock response with properly formatted detection results
        res.json({
            success: true,
            detections: [
                {
                    class: "person",
                    class_name: "person",
                    name: "person",
                    label: "person",
                    confidence: 0.85,
                    score: 0.85,
                    bbox: [100, 150, 200, 400],
                    box: [100, 150, 200, 400],
                    x: 100,
                    y: 150,
                    width: 100,
                    height: 250,
                    area: 25000
                },
                {
                    class: "car",
                    class_name: "car",
                    name: "car",
                    label: "car",
                    confidence: 0.92,
                    score: 0.92,
                    bbox: [300, 200, 500, 350],
                    box: [300, 200, 500, 350],
                    x: 300,
                    y: 200,
                    width: 200,
                    height: 150,
                    area: 30000
                },
                {
                    class: "bottle",
                    class_name: "bottle",
                    name: "bottle",
                    label: "bottle",
                    confidence: 0.78,
                    score: 0.78,
                    bbox: [450, 100, 480, 200],
                    box: [450, 100, 480, 200],
                    x: 450,
                    y: 100,
                    width: 30,
                    height: 100,
                    area: 3000
                }
            ],
            count: 3,
            processing_time: 0.045,
            image_size: [640, 480]
        });
    } catch (error) {
        res.status(500).json({ error: error.message, success: false });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: "healthy", port: PORT });
});

app.listen(PORT, () => {
    console.log(`YOLO Model Server running on port ${PORT}`);
    console.log(`Model info: http://localhost:${PORT}/model-info`);
    console.log(`Detection: http://localhost:${PORT}/detect`);
    console.log(`Health: http://localhost:${PORT}/health`);
});