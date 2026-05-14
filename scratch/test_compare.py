import requests

API = "http://localhost:8000"

def get_img(name, x_off=0, crop_l=0):
    payload = {
        "sequence": "क",
        "chars": [
            {
                "char": "क",
                "scale": 1.0,
                "x_offset": x_off,
                "y_offset": 0,
                "crop_top": 0,
                "crop_bottom": 0,
                "crop_left": crop_l,
                "crop_right": 0
            }
        ]
    }
    resp = requests.post(f"{API}/ligatures/preview", json=payload)
    with open(f"scratch/{name}.png", "wb") as f:
        f.write(resp.content)
    
get_img("base", 0, 0)
get_img("offset", -20, 0)
get_img("crop", 0, 20)
print("Done")
