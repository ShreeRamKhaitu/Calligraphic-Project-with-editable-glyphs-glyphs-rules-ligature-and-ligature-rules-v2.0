from PIL import Image, ImageDraw, ImageFont
font_path = "NithyaRanjanaDU-Regular.otf"
font = ImageFont.truetype(font_path, 80)
display_text = "च"
bb = font.getbbox(display_text)
w, h = bb[2]-bb[0], bb[3]-bb[1]
tw, th = w + 100, h + 100
temp_layer = Image.new("RGBA", (tw, th), color=(0,0,0,0))
temp_draw = ImageDraw.Draw(temp_layer)
tx, ty = (tw - w) // 2 - bb[0], (th - h) // 2 - bb[1]
temp_draw.text((tx, ty), display_text, font=font, fill=(0,0,0,255))

c_top = 17 # from user config
crop_y1 = ty + bb[1] + c_top
if crop_y1 > 0: temp_layer.paste((0,0,0,0), (0, 0, tw, crop_y1))

cluster_img = temp_layer.crop((tx + bb[0], ty + bb[1], tx + bb[2], ty + bb[3]))
print("Original bb:", bb)
print("tx, ty:", tx, ty)
print("crop_y1:", crop_y1)
print("cluster_img getbbox:", cluster_img.getbbox())
