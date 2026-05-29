import sys
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    """
    Test the health check endpoint returns 200 OK and correct JSON.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Hotel Booking AI Assistant"

def test_intent_router_high_confidence():
    """
    Test classifying an intent with high confidence (> 0.65 threshold).
    """
    mock_result = {"intent": "BOOK_ROOM", "confidence": 0.85}
    with patch("app.api.intent_router.classifier_service.classify_intent", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = mock_result
        
        response = client.post("/api/chat", json={"message": "I want to book a double room for two nights"})
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "BOOK_ROOM"
        assert data["confidence"] == 0.85
        mock_classify.assert_called_once_with("I want to book a double room for two nights")

def test_intent_router_low_confidence_fallback():
    """
    Test classifying an intent with low confidence (< 0.65 threshold)
    and check if it falls back to 'clarification_required'.
    """
    mock_result = {"intent": "GUEST_REQUEST", "confidence": 0.42}
    with patch("app.api.intent_router.classifier_service.classify_intent", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = mock_result
        
        response = client.post("/api/chat", json={"message": "need stuff"})
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "clarification_required"
        assert data["confidence"] == 0.42
        mock_classify.assert_called_once_with("need stuff")

def test_intent_router_invalid_payload():
    """
    Test that invalid schema payloads return a 422 Unprocessable Entity error.
    """
    response = client.post("/api/chat", json={"invalid_field": "test"})
    assert response.status_code == 422

def run_tests():
    print("=" * 60)
    print("STARTING FASTAPI ASSISTANT SERVICE TESTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    tests = [
        ("Health Check Endpoint", test_health_check),
        ("High Confidence Classification", test_intent_router_high_confidence),
        ("Low Confidence Fallback Threshold", test_intent_router_low_confidence_fallback),
        ("Invalid Payload Schema Validation", test_intent_router_invalid_payload),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")
            failed += 1
            
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
