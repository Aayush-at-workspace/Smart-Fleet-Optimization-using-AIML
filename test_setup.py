import os
import requests
import json

def test_system():
    # Check directory structure
    required_dirs = ['static/css', 'static/js', 'models', 'templates']
    for d in required_dirs:
        if not os.path.exists(d):
            print(f"Missing directory: {d}")
            return False

    # Check required files
    required_files = [
        'static/css/style.css',
        'static/js/main.js',
        'templates/index.html',
        'rides.csv'
    ]
    for f in required_files:
        if not os.path.exists(f):
            print(f"Missing file: {f}")
            return False

    # Test API endpoint
    try:
        response = requests.post(
            'http://localhost:5000/complete_ride',
            json={
                "cab_id": "TEST_001",
                "pickup": "Delhi",
                "drop": "Noida",
                "drop_time": "2025-04-26T14:30:00"
            }
        )
        print("API Response:", response.json())
        return True
    except Exception as e:
        print(f"API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    if test_system():
        print("System setup verified successfully!")
    else:
        print("System setup needs attention!") 