import requests

API = "http://localhost:8000"

def test_crop_alignment():
    # Render with no crop
    payload_no_crop = {
        "char": "क",
        "type": "full",
        "scale": 1.0,
        "x_offset": 0,
        "y_offset": 0,
        "crop_top": 0,
        "crop_bottom": 0,
        "crop_left": 0,
        "crop_right": 0
    }
    resp1 = requests.post(f"{API}/glyphs/preview", json=payload_no_crop)
    with open("scratch/crop_test_none.png", "wb") as f:
        f.write(resp1.content)

    # Render with crop
    payload_crop = {
        "char": "क",
        "type": "full",
        "scale": 1.0,
        "x_offset": 0,
        "y_offset": 0,
        "crop_top": 20, # Crop 20px from top
        "crop_bottom": 0,
        "crop_left": 0,
        "crop_right": 0
    }
    resp2 = requests.post(f"{API}/glyphs/preview", json=payload_crop)
    with open("scratch/crop_test_top.png", "wb") as f:
        f.write(resp2.content)
    
    print("Crop test images saved to scratch/")

if __name__ == "__main__":
    test_crop_alignment()
