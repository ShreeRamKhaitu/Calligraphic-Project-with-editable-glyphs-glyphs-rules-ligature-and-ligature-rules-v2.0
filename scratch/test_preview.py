import requests

payload = {
    "sequence": "क",
    "chars": [
        {
            "char": "क",
            "scale": 1.0,
            "x_offset": 0,
            "y_offset": 0,
            "crop_top": 0,
            "crop_bottom": 0,
            "crop_left": 0,
            "crop_right": 0
        }
    ]
}
resp = requests.post("http://localhost:8000/ligatures/preview", json=payload)
with open("scratch/preview_test_nocrop.png", "wb") as f:
    f.write(resp.content)
