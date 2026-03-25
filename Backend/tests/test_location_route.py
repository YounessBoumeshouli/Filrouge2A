import pytest
import sys
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def dummy_image():
    return b"dummy_image_content"

def test_analyze_location_invalid_file(client, dummy_image):
    files = {"file": ("test_doc.txt", b"hello world", "text/plain")}
    
    response = client.post("/api/location/analyze", files=files)
    
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]

def test_analyze_location_ai_service_error(client, dummy_image):
    with patch("app.services.ai_service.AIService.analyze_location", side_effect=Exception("API limit reached")):
        files = {"file": ("test_image.jpg", dummy_image, "image/jpeg")}
        
        response = client.post("/api/location/analyze", files=files)
        
        assert response.status_code == 500
        assert "API limit reached" in response.json()["detail"]

def test_analyze_location_missing_file(client):
    response = client.post("/api/location/analyze")
    
    assert response.status_code == 422 
