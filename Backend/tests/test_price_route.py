import pytest
from unittest.mock import patch

@pytest.fixture
def dummy_image():
    return b"dummy_image_content"

def test_analyze_price_success_file(client, dummy_image):
    # Request files matching expected format
    files = {"file": ("test_item.jpg", dummy_image, "image/jpeg")}
    
    # We patch the model prediction if it is loaded (to avoid real model inference time)
    # The actual behavior depends heavily on whether model_api is loaded, but its fallback logic works
    
    # Even if model_api is bypassed by a mock, at least it tests the endpoints logic
    with patch("app.routers.price.model_api") as mock_model:
        if mock_model is not None:
            mock_model.predict_from_base64.return_value = {
                "success": True,
                "product_type": "leather",
                "confidence": 0.85,
                "message": "Looks like leather"
            }
            
        response = client.post("/api/price/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

def test_analyze_price_success_base64(client):
    # Create base64 string directly
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    with patch("app.routers.price.model_api") as mock_model:
        if mock_model is not None:
            mock_model.predict_from_base64.return_value = {
                "success": True, 
                "product_type": "textiles"
            }
        
        response = client.post("/api/price/analyze", data={"image": dummy_b64})
        
        assert response.status_code == 200
        assert response.json()["success"] is True

def test_analyze_price_missing_input(client):
    # Sending neither file nor image base64
    response = client.post("/api/price/analyze")
    
    assert response.status_code == 400
    assert "Either file or image data required" in response.json()["detail"]

def test_analyze_price_invalid_file(client):
    # Send a text file instead of image
    files = {"file": ("document.pdf", b"pdf content", "application/pdf")}
    
    response = client.post("/api/price/analyze", files=files)
    
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]

def test_analyze_price_exception(client, dummy_image):
    files = {"file": ("test.jpg", dummy_image, "image/jpeg")}
    
    # Force an exception during image processing/reading manually or by patching
    # Here we mock the `file.read` operation on Fastapi UploadFile or use a patched route
    with patch("app.routers.price.base64.b64encode", side_effect=Exception("Base64 encode failed")):
        response = client.post("/api/price/analyze", files=files)
        
        assert response.status_code == 500
        assert "Base64 encode failed" in response.json()["detail"]
