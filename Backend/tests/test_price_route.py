import pytest
from unittest.mock import patch


@pytest.fixture
def dummy_image():
    return b"dummy_image_content"


def test_analyze_price_success_file(client, dummy_image):
    files = {"file": ("test_item.jpg", dummy_image, "image/jpeg")}

    with patch("app.routers.price.model_api") as mock_model:
        mock_model.predict_from_base64.return_value = {
            "success": True,
            "product_type": "leather",
            "confidence": 0.85,
            "message": "Looks like leather",
        }
        response = client.post("/api/price/analyze", files=files)

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_analyze_price_success_base64(client):
    dummy_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

    with patch("app.routers.price.model_api") as mock_model:
        mock_model.predict_from_base64.return_value = {
            "success": True,
            "product_type": "textiles",
        }
        response = client.post("/api/price/analyze", json={"image": dummy_b64})

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_analyze_price_missing_input(client):
    response = client.post("/api/price/analyze")

    assert response.status_code == 400
    assert "Either file or image data required" in response.json()["detail"]


def test_analyze_price_invalid_file(client):
    files = {"file": ("document.pdf", b"pdf content", "application/pdf")}
    response = client.post("/api/price/analyze", files=files)

    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]


def test_analyze_price_exception(client, dummy_image):
    files = {"file": ("test.jpg", dummy_image, "image/jpeg")}

    with patch(
        "app.routers.price.base64.b64encode",
        side_effect=Exception("Base64 encode failed"),
    ):
        response = client.post("/api/price/analyze", files=files)

    assert response.status_code == 500
    assert "Base64 encode failed" in response.json()["detail"]
