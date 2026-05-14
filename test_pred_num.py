from PIL import Image, ImageDraw, ImageFont
import numpy as np
import joblib
import sys

def test_prediction(char, expected_class, expected_deva):
    size = (64, 64)
    font_path = "NithyaRanjanaDU-Regular.otf"
    
    image = Image.new('L', size, color=255)
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype(font_path, 40)
    bbox = draw.textbbox((0, 0), char, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    x = (size[0] - w) / 2 - bbox[0]
    y = (size[1] - h) / 2 - bbox[1]
    
    draw.text((x, y), char, font=font, fill=0)
    
    # Process for model
    img_array = np.array(image).flatten() / 255.0
    img_array = img_array.reshape(1, -1)
    
    # Predict
    model = joblib.load("ranjana_rf_model.pkl")
    with open("classes.txt", "r", encoding='utf-8') as f:
        class_names = f.read().splitlines()
        
    prediction = model.predict(img_array)
    probs = model.predict_proba(img_array)
    confidence = np.max(probs)
    
    class_idx = prediction[0]
    predicted_label = class_names[class_idx]
    
    print(f"Testing Character/Deva: {char}/{expected_deva}")
    print(f"Predicted class label: {predicted_label} | Expected folder: {expected_class}")
    print(f"Confidence: {confidence:.2f}")
    if predicted_label == expected_class:
        print("PASS\n")
    else:
        print("FAIL\n")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    # Test number 4
    test_prediction('४', '4', '४')
    # Test symbol ?
    test_prediction('?', 'question', '?')
