from PIL import Image, ImageDraw

img = Image.new("RGBA", (400, 400), (0,0,0,0))
char_layer = Image.new("RGBA", (200, 200), (0,0,0,0))
draw = ImageDraw.Draw(char_layer)
draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0, 255))

x_offset = 20 # User moves character 20px right
x_pos = (400 - 200) // 2 + x_offset
y_pos = 100
img.paste(char_layer, (x_pos, y_pos), char_layer)

final_bbox = img.getbbox()
final_img = img.crop(final_bbox)
print(f"Final img size: {final_img.size}")
