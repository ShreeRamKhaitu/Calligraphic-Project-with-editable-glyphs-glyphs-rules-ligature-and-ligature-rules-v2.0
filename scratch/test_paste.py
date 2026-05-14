from PIL import Image
img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
img.paste((0, 0, 0, 0), (0, 0, 100, 50))
print(img.getpixel((50, 25)))
print(img.getpixel((50, 75)))
