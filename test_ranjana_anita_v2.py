from PIL import Image, ImageDraw, ImageFont
import os
import re
import sys

# Ensure UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def render_test_multiline(text, filename):
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 100
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Font load failed: {e}")
        return

    # Split into clusters
    cluster_regex = r'[\u0905-\u0939\u0958-\u095F](?:[\u094D][\u0905-\u0939\u0958-\u095F])*[\u093E-\u094C\u094D\u0901-\u0903]?|[\u0905-\u0914]'
    clusters = re.findall(cluster_regex, text)
    print(f"Clusters: {clusters}")
    
    # Create multiline text
    multiline_text = "\n".join(clusters)
    
    img = Image.new('RGB', (400, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use multiline_text in a single call to see if it preserves shaping better
    draw.text((50, 50), multiline_text, font=font, fill='black', spacing=20)

    img.save(filename)
    print(f"Saved {filename}")

if __name__ == "__main__":
    text = "अनिता" 
    render_test_multiline(text, "test_anita_multiline.png")
