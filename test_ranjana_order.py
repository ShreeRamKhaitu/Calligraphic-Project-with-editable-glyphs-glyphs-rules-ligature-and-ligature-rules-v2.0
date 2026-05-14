from PIL import Image, ImageDraw, ImageFont
import os
import sys

# Ensure UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def render_variations(output_name):
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 80
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Font load failed: {e}")
        return

    # Variations of "Ni"
    variations = [
        ("न + ि (Logical)", "\u0928\u093F"),
        ("ि + न (Visual)", "\u093F\u0928"),
        ("न + ा (For comparison)", "\u0928\u093E"),
        ("अ + न + ि (With context)", "\u0905\u0928\u093F"),
        ("Space + न + ि", " \u0928\u093F"),
    ]

    img = Image.new('RGB', (600, 500), color='white')
    draw = ImageDraw.Draw(img)
    
    y = 50
    for label, text in variations:
        draw.text((20, y), label, fill='gray')
        draw.text((300, y), text, font=font, fill='black')
        print(f"Rendered {label}: {text.encode('unicode_escape')}")
        y += 80

    img.save(output_name)
    print(f"Saved {output_name}")

if __name__ == "__main__":
    render_variations("test_ni_variations.png")
