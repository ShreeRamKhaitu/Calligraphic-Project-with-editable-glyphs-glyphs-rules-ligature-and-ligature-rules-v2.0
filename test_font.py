from PIL import Image, ImageDraw, ImageFont
import os

def test_render():
    font_path = "NithyaRanjanaDU-Regular.otf"
    # क + ् + क
    text = "\u0915\u094D\u0915" 
    font_size = 80
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Font load failed: {e}")
        return

    # Check rendering
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), text, font=font, fill='black')
    img.save("test_halant.png")
    print("Test image saved as test_halant.png")

if __name__ == "__main__":
    test_render()
