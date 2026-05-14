import numpy as np
import joblib
from PIL import Image, ImageOps
import sys
import os

def predict(image_path):
    # Load model and classes
    model_path = "ranjana_rf_model.pkl"
    class_path = "classes.txt"
    
    if not os.path.exists(model_path) or not os.path.exists(class_path):
        print("Model or classes file not found. Run train.py first.")
        return

    model = joblib.load(model_path)
    with open(class_path, "r") as f:
        class_names = f.read().splitlines()

    # Load and preprocess image
    try:
        img = Image.open(image_path).convert('L')
        # Invert if it's black ink on white paper (assuming training was white ink on black or vice versa)
        # data_gen.py creates black text on white bg (0 on 255)
        # Random Forest sees 0 for text and 1 for background if normalized or vice versa.
        # Let's ensure consistency.
        img = img.resize((64, 64))
        img_array = np.array(img).flatten() / 255.0
        img_array = img_array.reshape(1, -1)
    except Exception as e:
        print(f"Error processing image: {e}")
        return

    # Predict
    prediction = model.predict(img_array)
    probs = model.predict_proba(img_array)
    confidence = np.max(probs)
    
    class_idx = prediction[0]
    print(f"Predicted: {class_names[class_idx]} with confidence {confidence:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test.py <image_path>")
    else:
        predict(sys.argv[1])
