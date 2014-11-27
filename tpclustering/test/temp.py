from PIL import Image
import sys


out_filename = "D:/out2.txt"
img_filename = "D:/b1.png"
r_min = 0
r_max = 100
g_min = 0
g_max = 100
b_min = 0
b_max = 100

im = Image.open(img_filename)

imageW = im.size[0]
imageH = im.size[1]

f = open(out_filename, 'w')

for j in range(0, imageH):
    for i in range(0, imageW):
        coordinate = (i, j)
        pixel = im.getpixel(coordinate)
        if(pixel[0]>=r_min and pixel[0]<r_max
           and pixel[1] >= g_min and pixel[1] < g_max
           and pixel[2] >= b_min and pixel[2] < b_max):
            f.write("1")
        else:
            f.write("0")
    f.write("\n")