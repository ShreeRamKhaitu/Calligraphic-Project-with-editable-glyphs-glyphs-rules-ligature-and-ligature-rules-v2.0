import requests
import json

API = "http://localhost:8000"

def test_ligature_preview():
    payload = {
        "sequence": "क+र",
        "chars": [
            {"char": "क", "scale": 1.0, "x_offset": 0, "y_offset": 0, "y_advance": 50},
            {"char": "र", "scale": 0.8, "x_offset": 10, "y_offset": 0, "y_advance": 80}
        ]
    }
    resp = requests.post(f"{API}/ligatures/preview", json=payload)
    if resp.status_code == 200:
        with open("scratch/test_ligature_preview.png", "wb") as f:
            f.write(resp.content)
        print("Ligature preview saved to scratch/test_ligature_preview.png")
    else:
        print(f"Ligature preview failed: {resp.status_code} - {resp.text}")

def test_monogram_with_ligature():
    # First save the ligature rule
    rule = {
        "sequence": "क+र",
        "chars": [
            {"char": "क", "scale": 1.0, "x_offset": 0, "y_offset": 0, "y_advance": 40},
            {"char": "र", "scale": 0.7, "x_offset": 0, "y_offset": -10, "y_advance": 60}
        ]
    }
    requests.post(f"{API}/ligatures/save", json=rule)
    
    # Then generate monogram
    payload = {
        "text": "क र", # The backend splits by space or re-findall. 
                       # Wait, how does it match ligatures? 
                       # In api.py, it uses re.findall(CLUSTER_REGEX, text) if vertical.
                       # Then it merges clusters based on lig_configs.
                       # "क+र" would match if the clusters are "क" and "र".
        "font_size": 80,
        "vertical": True,
        "use_overrides": True
    }
    resp = requests.post(f"{API}/monogram", json=payload)
    if resp.status_code == 200:
        with open("scratch/test_monogram_ligature.png", "wb") as f:
            f.write(resp.content)
        print("Monogram with ligature saved to scratch/test_monogram_ligature.png")
    else:
        print(f"Monogram failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    test_ligature_preview()
    test_monogram_with_ligature()
