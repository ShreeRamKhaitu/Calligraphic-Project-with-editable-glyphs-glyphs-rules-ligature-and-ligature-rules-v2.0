import requests

configs = {
    "k": {
        "full": {
            "crop_bottom": 50,
            "scale": 1.0
        }
    },
    "r": {
        "full": {
            "crop_top": 50,
            "scale": 1.0
        }
    }
}

with open("glyph_configs.json", "w", encoding="utf-8") as f:
    import json
    json.dump(configs, f)

req = {
    "text": "k*ra",
    "font_size": 100,
    "line_spacing": 0,
    "use_overrides": True
}
res = requests.post("http://localhost:8000/monogram", json=req)
if res.status_code == 200:
    with open("scratch/test_monogram.png", "wb") as f:
        f.write(res.content)
    print("Success")
else:
    print(res.text)
