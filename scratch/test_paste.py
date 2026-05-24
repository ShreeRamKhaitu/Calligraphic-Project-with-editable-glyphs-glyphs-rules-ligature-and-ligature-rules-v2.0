from PIL import Image, ImageDraw

img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([20, 20, 80, 80], fill=(255, 0, 0, 255))

part = img.crop((20, 20, 50, 50))
img.paste((0,0,0,0), (20, 20, 50, 50))
img.paste(part, (50, 50), part)

img.save("test_paste_result.png")
