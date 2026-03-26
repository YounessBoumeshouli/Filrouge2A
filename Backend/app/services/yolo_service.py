"""
YOLO-Nano Detection Service
Integrates the trained YOLO-Nano model for object detection
"""

try:
    import torch
    import cv2
    import numpy as np
    from pathlib import Path
    import yaml
    from PIL import Image
    import io
    import base64

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ YOLO dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False
    torch = cv2 = np = Path = yaml = Image = io = base64 = None


class YOLONanoService:
    """YOLO-Nano detection service"""

    def __init__(self, model_path=None, config_path=None):
        if not DEPENDENCIES_AVAILABLE:
            print("⚠️ YOLO service disabled - missing dependencies")
            self.model = None
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.class_names = []
        self.img_size = 416
        self.conf_thres = 0.25
        self.iou_thres = 0.45

        # Default paths
        if model_path is None:
            model_path = (
                Path(__file__).parent.parent.parent
                / "Ai"
                / "yolo-nano"
                / "runs"
                / "train"
                / "exp"
                / "best.pt"
            )
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent.parent
                / "Ai"
                / "yolo-nano"
                / "configs"
                / "yolo_nano.yaml"
            )

        self.load_model(model_path, config_path)

    def load_model(self, model_path, config_path):
        """Load the trained YOLO-Nano model"""
        if not DEPENDENCIES_AVAILABLE:
            return

        try:
            # Import YOLO-Nano components
            import sys

            sys.path.append(
                str(Path(__file__).parent.parent.parent / "Ai" / "yolo-nano")
            )

            from utils.models import YOLONano

            # Load config
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            self.class_names = config["data"]["names"]
            self.img_size = config["model"]["input_size"][0]

            # Create model
            self.model = YOLONano(
                num_classes=len(self.class_names), img_size=self.img_size
            ).to(self.device)

            # Load weights
            if Path(model_path).exists():
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.model.eval()
                print(f"✓ YOLO-Nano model loaded from {model_path}")
            else:
                print(f"⚠ Model file not found: {model_path}")
                print(
                    "Please train the model first using: python train.py --epochs 100"
                )

        except Exception as e:
            print(f"✗ Error loading YOLO-Nano model: {e}")
            self.model = None

    def preprocess_image(self, image):
        """Preprocess image for YOLO-Nano"""
        if not DEPENDENCIES_AVAILABLE:
            return None, None, None

        # Convert PIL Image to numpy array
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Resize image
        h, w = image.shape[:2]
        img_resized = cv2.resize(image, (self.img_size, self.img_size))

        # Convert to RGB and normalize
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)

        return img_tensor, image, (h, w)

    def detect_objects(self, image, conf_thres=None, iou_thres=None):
        """Detect objects in image"""
        if not DEPENDENCIES_AVAILABLE:
            return {
                "success": False,
                "error": "YOLO dependencies not available. Install opencv-python, torch, and other requirements.",
                "detections": [],
            }

        if self.model is None:
            return {
                "success": False,
                "error": "Model not loaded. Please train the model first.",
                "detections": [],
            }

        try:
            # Import YOLO utilities
            import sys

            sys.path.append(
                str(Path(__file__).parent.parent.parent / "Ai" / "yolo-nano")
            )
            from utils.general import non_max_suppression, scale_coords

            conf_thres = conf_thres or self.conf_thres
            iou_thres = iou_thres or self.iou_thres

            # Preprocess image
            img_tensor, img_orig, orig_shape = self.preprocess_image(image)

            # Run inference
            with torch.no_grad():
                pred = self.model(img_tensor)

            # Apply NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, max_det=100)

            detections = []
            if len(pred) > 0 and pred[0] is not None:
                det = pred[0]

                # Scale coordinates to original image
                det[:, :4] = scale_coords(
                    (self.img_size, self.img_size), det[:, :4], orig_shape
                )

                for *xyxy, conf, cls in det:
                    x1, y1, x2, y2 = [int(x.item()) for x in xyxy]
                    confidence = conf.item()
                    class_id = int(cls.item())
                    class_name = (
                        self.class_names[class_id]
                        if class_id < len(self.class_names)
                        else f"class_{class_id}"
                    )

                    detections.append(
                        {
                            "bbox": [x1, y1, x2, y2],
                            "confidence": round(confidence, 3),
                            "class_id": class_id,
                            "class_name": class_name,
                            "category": "monument" if class_id <= 9 else "product",
                        }
                    )

            return {
                "success": True,
                "detections": detections,
                "image_size": orig_shape,
                "model_info": {
                    "classes": len(self.class_names),
                    "conf_threshold": conf_thres,
                    "iou_threshold": iou_thres,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "detections": []}

    def visualize_detections(self, image, detections):
        """Draw bounding boxes on image"""
        if isinstance(image, Image.Image):
            image = np.array(image)

        img_vis = image.copy()

        # Color map for different categories
        colors = {
            "monument": (0, 255, 0),  # Green
            "product": (255, 0, 0),  # Red
            "default": (0, 0, 255),  # Blue
        }

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            class_name = det["class_name"]
            category = det.get("category", "default")

            # Choose color based on category
            color = colors.get(category, colors["default"])

            # Draw bounding box
            cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{class_name} {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(
                img_vis,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1,
            )
            cv2.putText(
                img_vis,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return img_vis

    def process_image_base64(self, image_base64, conf_thres=None, iou_thres=None):
        """Process base64 encoded image"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(
                image_base64.split(",")[1] if "," in image_base64 else image_base64
            )
            image = Image.open(io.BytesIO(image_data))

            # Detect objects
            result = self.detect_objects(image, conf_thres, iou_thres)

            # Add visualization if successful
            if result["success"] and result["detections"]:
                img_with_boxes = self.visualize_detections(image, result["detections"])

                # Convert back to base64
                img_pil = Image.fromarray(
                    cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB)
                )
                buffer = io.BytesIO()
                img_pil.save(buffer, format="JPEG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()

                result["visualized_image"] = f"data:image/jpeg;base64,{img_base64}"

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}",
                "detections": [],
            }


# Global service instance
yolo_service = None


def get_yolo_service():
    """Get the YOLO-Nano service instance"""
    global yolo_service
    if yolo_service is None:
        yolo_service = YOLONanoService()
    return yolo_service
