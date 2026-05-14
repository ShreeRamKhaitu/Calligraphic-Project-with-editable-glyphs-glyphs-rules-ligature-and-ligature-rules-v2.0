from PIL import Image, ImageDraw, ImageFont
import numpy as np
import joblib
import sys

def test_halant_prediction():
    # 1. Generate a halant image just like the dataset
    char = '्'
    display_char = '◌' + char
    size = (64, 64)
    font_path = "NithyaRanjanaDU-Regular.otf"
    
    image = Image.new('L', size, color=255)
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype(font_path, 40)
    bbox = draw.textbbox((0, 0), display_char, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    x = (size[0] - w) / 2 - bbox[0]
    y = (size[1] - h) / 2 - bbox[1]
    
    draw.text((x, y), display_char, font=font, fill=0)
    
    # Optional save to inspect visually
    image.save("test_single_halant.png")
    
    # 2. Process for the model
    img_array = np.array(image).flatten() / 255.0
    img_array = img_array.reshape(1, -1)
    
    # 3. Predict
    model = joblib.load("ranjana_rf_model.pkl")
    with open("classes.txt", "r", encoding='utf-8') as f:
        class_names = f.read().splitlines()
        
    prediction = model.predict(img_array)
    probs = model.predict_proba(img_array)
    confidence = np.max(probs)
    
    class_idx = prediction[0]
    predicted_label = class_names[class_idx]
    
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        
    print(f"Predicted class: {predicted_label} | Expected: halant or * (* usually)")
    print(f"Confidence: {confidence:.2f}")
    if predicted_label == "halant" or predicted_label == "*":
        print("PASS")
    else:
        print("FAIL")

if __name__ == "__main__":
    test_halant_prediction()
