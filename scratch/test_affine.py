from PIL import Image, ImageDraw

img = Image.new("RGBA", (100, 100), (0,0,0,0))
draw = ImageDraw.Draw(img)
draw.rectangle([40, 20, 60, 80], fill=(255, 0, 0, 255)) # vertical rectangle

w, h = img.size
x_c, y_c = w/2, h/2
skew_x = 0.5
a = 1
b = -skew_x
cx = skew_x * y_c
img_skew = img.transform((w, h), Image.AFFINE, (a, b, cx, 0, 1, 0))
img_skew.save("scratch/test_skewed.png")
