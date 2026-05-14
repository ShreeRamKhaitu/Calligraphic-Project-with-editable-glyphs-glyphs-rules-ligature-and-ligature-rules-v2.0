from PIL import Image, ImageDraw, ImageFont
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def render_test(text, filename, vertical=False):
    font_path = "NithyaRanjanaDU-Regular.otf"
    font_size = 100
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Font load failed: {e}")
        return

    if vertical:
        # Simple vertical stack logic
        import re
        cluster_regex = r'[\u0905-\u0939\u0958-\u095F](?:[\u094D][\u0905-\u0939\u0958-\u095F])*[\u093E-\u094C\u094D\u0901-\u0903]?|[\u0905-\u0914]'
        clusters = re.findall(cluster_regex, text)
        print(f"Clusters for {text}: {clusters}")
        lines = clusters if clusters else list(text)
    else:
        lines = [text]

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    
    img_w = 400
    img_h = line_height * len(lines) + 100
    
    img = Image.new('RGB', (img_w, img_h), color='white')
    draw = ImageDraw.Draw(img)
    
    y = 50
    for line in lines:
        # Use draw.text with default anchor
        draw.text((50, y), line, font=font, fill='black')
        y += line_height + 10

    img.save(filename)
    print(f"Saved {filename}")

if __name__ == "__main__":
    text = "अनिता" # anitaa
    render_test(text, "test_anita_horizontal.png", vertical=False)
    render_test(text, "test_anita_vertical.png", vertical=True)
