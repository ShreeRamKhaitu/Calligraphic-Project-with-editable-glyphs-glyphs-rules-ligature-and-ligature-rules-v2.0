import requests

configs = {
    "k": {
        "first": {
            "crop_bottom": 50,
            "scale": 1.0
        },
        "middle": {
            "crop_top": 20,
            "crop_bottom": 20,
            "scale": 1.0
        },
        "last": {
            "crop_top": 50,
            "scale": 1.0
        }
    }
}

with open("glyph_configs.json", "w", encoding="utf-8") as f:
    import json
    json.dump(configs, f)

req = {
    "text": "kkk",
    "font_size": 100,
    "line_spacing": 0,
    "use_overrides": True
}
res = requests.post("http://localhost:8000/monogram", json=req)
print(res.status_code)
