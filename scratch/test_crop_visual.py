from PIL import Image, ImageDraw

# Create 400x400 canvas
img = Image.new("RGBA", (400, 400), (0,0,0,0))
# Create character layer 200x200
char_layer = Image.new("RGBA", (200, 200), (0,0,0,0))
draw = ImageDraw.Draw(char_layer)
# Draw a rectangle as character from 50,50 to 150,150
draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0, 255))

crop_left = 20
bbox = char_layer.getbbox()
bl, bt, br, bb_y = bbox
cw_layer, ch_layer = char_layer.size

# Apply crop left 20
char_layer.paste((0,0,0,0), (0, 0, bl + crop_left, ch_layer))

x_pos = (400 - 200) // 2
y_pos = 100
img.paste(char_layer, (x_pos, y_pos), char_layer)

final_bbox = img.getbbox()
final_img = img.crop(final_bbox)
print(f"Original bbox: {bbox}")
print(f"Final bbox of img: {final_bbox}")
print(f"Final img size: {final_img.size}")
