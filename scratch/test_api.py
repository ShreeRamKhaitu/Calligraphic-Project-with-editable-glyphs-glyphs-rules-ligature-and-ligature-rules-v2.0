import requests
import json

payload = {
    "sequence": "क+र",
    "chars": [
        {
            "char": "क",
            "skew_x": 0.5,
            "skew_y": 0.0,
            "crop_top": 50,
            "crop_bottom": 0,
            "crop_left": 10,
            "crop_right": 0
        }
    ]
}
try:
    resp = requests.post("http://localhost:8000/ligatures/preview", json=payload)
    print(resp.status_code)
except Exception as e:
    print(e)
