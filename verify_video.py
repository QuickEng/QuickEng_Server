import requests
import json
import time

def test_analyze():
    url = "http://127.0.0.1:8000/v1/video/analyze"
    # A short video or one with transcripts enabled.
    # https://www.youtube.com/watch?v=jNQXAC9IVRw (Me at the zoo - very short)
    payload = {
        "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "language": "en"
    }
    
    print(f"Sending request to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("Response received successfully!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Validation
        assert "video_url" in data
        assert "script" in data
        assert isinstance(data["script"], list)
        if len(data["script"]) > 0:
            assert "text" in data["script"][0]
            assert "start" in data["script"][0]
        
        assert "words" in data
        assert isinstance(data["words"], list)
        if len(data["words"]) > 0:
            assert "word" in data["words"][0]
            assert "meaning" in data["words"][0]
            assert "example" in data["words"][0]
            
        print("Verification PASSED!")
        
    except Exception as e:
        print(f"Verification FAILED: {e}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")

if __name__ == "__main__":
    # Wait a bit for server to start if running immediately after
    time.sleep(2)
    test_analyze()
