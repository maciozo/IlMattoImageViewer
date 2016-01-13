#!/usr/bin/env python

from PIL import Image
import time

mode = 2
#0 = 30x40x16   (RGB565, greyscale)
#1 = 48x64x8    (RGB332, greyscale)
#2 = 60x80x4    (RGB121, greyscale)
#3 = 120x160x2  (greyscale)

rotateAngle = 0

greyscale = False
#Precise up to 8 bits

im = Image.open("image.bmp")
#RGB888

if rotateAngle:
    im = im.rotate(rotateAngle)
    
# x and y are the dimensions of each image pixel in terms of actual pixels on the LCD.
if (mode == 0):
    width = 30
    height = 40
    x = 8
    y = 8
elif (mode == 1):
    width = 48
    height = 64
    x = 5
    y = 5
elif (mode == 2):
    width = 60
    height = 80
    x = 4
    y = 4
elif (mode == 3):
    width = 120
    height = 160
    x = 2
    y = 2
    greyscale = True
if (greyscale):
    im = im.convert("L")
    
im = im.resize((width, height), Image.BICUBIC)

pixels = list(im.getdata())

mode0str = """\
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "./lcdlib/lcd.h"
int main()
{
    uint16_t x, y, column, row = 0;
    rectangle pixel;
    uint16_t pixelData[%d][%d] PROGMEM = !BMP_DATA!;
    init_lcd();
    for (x = 0; x < 240; x += %d)
    {
        column = 0;
        for (y = 0; y < 320; y += %d)
        {
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            fill_rectangle(pixel, pixelData[row][column]);
            column++;
        }
        row++;
    }
}
""" % (width, height, x, y, x, y)

mode0gstr = """\
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "./lcdlib/lcd.h"
int main()
{
    uint16_t x, y, column, row = 0, greyPixel = 0;
    rectangle pixel;
    uint8_t pixelData[%d][%d] PROGMEM = !BMP_DATA!;
    init_lcd();
    for (x = 0; x < 240; x += %d)
    {
        column = 0;
        for (y = 0; y < 320; y += %d)
        {
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            greyPixel = ((pixelData[row][column] / 8) << 11) + ((pixelData[row][column] / 4) << 5) + (pixelData[row][column] / 8);
            fill_rectangle(pixel, greyPixel);
            column++;
        }
        row++;
    }
}
""" % (width, height, x, y, x, y)

mode1str = """\
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "./lcdlib/lcd.h"
int main()
{
    uint16_t x, y, column, row = 0, colour = 0;
    uint16_t r, g, b;
    rectangle pixel;
    uint8_t pixelData[%d][%d] PROGMEM = !BMP_DATA!;
    init_lcd();
    for (x = 0; x < 240; x += %d)
    {
        column = 0;
        for (y = 0; y < 320; y += %d)
        {
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            r = 0;
            g = 0; 
            b = 0;
            
            //RGB332 -> RGB565
            r = (pixelData[row][column] >> 5) << 13;
            g = ((pixelData[row][column] >> 2) & 0b00000111) << 8;
            b = ((pixelData[row][column]) & 0b00000011) << 3;
            colour = (r | g | b);
            
            fill_rectangle(pixel, colour);
            column++;
        }
        row++;
    }
}
""" % (width, height, x, y, x, y)

mode1gstr = """\
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "./lcdlib/lcd.h"
int main()
{
    uint16_t x, y, column, row = 0, greyPixel = 0;
    rectangle pixel;
    uint8_t pixelData[%d][%d] PROGMEM = !BMP_DATA!;
    init_lcd();
    for (x = 0; x < 240; x += %d)
    {
        column = 0;
        for (y = 0; y < 320; y += %d)
        {
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            greyPixel = ((pixelData[row][column] / 8) << 11) + ((pixelData[row][column] / 4) << 5) + (pixelData[row][column] / 8);
            fill_rectangle(pixel, greyPixel);
            column++;
        }
        row++;
    }
}
""" % (width, height, x, y, x, y)

mode2str = """\
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "./lcdlib/lcd.h"
int main()
{
    uint16_t x, y, column, row = 0, colour = 0;
    uint16_t r, g, b;
    rectangle pixel;
    uint8_t pixelData[%d][%d] PROGMEM = !BMP_DATA!;
    init_lcd();
    for (x = 0; x < 240; x += %d)
    {
        column = 0;
        for (y = 0; y < 320; y += %d)
        {
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            r = 0;
            g = 0; 
            b = 0;
            
            //RGB121 -> RGB565
            colour = pixelData[row][column] >> 4;
            r = ((colour & 0b1000) >> 3) << 15;
            g = ((colour & 0b0110) >> 1) << 9;
            b = (colour & 0b0001) << 4;
            colour = (r | g | b);
            
            fill_rectangle(pixel, colour);
            column++;
            y++;
            
            pixel.left = x;
            pixel.right = x + %d;
            pixel.top = y;
            pixel.bottom = y + %d;
            r = 0;
            g = 0; 
            b = 0;
            
            //RGB121 -> RGB565
            colour = pixelData[row][column] & 0b00001111;
            r = ((colour & 0b1000) >> 3) << 15;
            g = ((colour & 0b0110) >> 1) << 9;
            b = (colour & 0b0001) << 4;
            colour = (r | g | b);
            
            fill_rectangle(pixel, colour);
            column++;
            
        }
        row++;
    }
}
""" % (width/2, height/2, x, y, x, y, x, y)



column = 0;
row = 0;

pixelGrid = [];
for i in range(0, width):
    new = []
    for j in range(0, height - 1):
        new.append(0)
    pixelGrid.append(new)

def mode0():
    pixel = 0;
    # print(pixels)
    for row in range(0, height - 1):
        for col in range(0, width):
            rgb = pixels[pixel]
            # print(rgb)
            red = rgb[0]
            green = rgb[1]
            blue = rgb[2]
            
            #RGB888 -> RGB565
            rgb = ((int(red / 255 * 31) << 11) | (int(green / 255 * 63) << 5) | (int(blue / 255 * 31)))
            
            pixelGrid[col][row] = hex(rgb)
            pixel += 1

    for item in pixelGrid:
        open("output.c", "w")
        with open("output.c", "a") as file:
            file.write(mode0str.replace("!BMP_DATA!", str(pixelGrid).replace("[", "{").replace("]", "}").replace("'", "")))
            
def mode0g():
    pixel = 0;
    # print(pixels)
    for row in range(0, height - 1):
        for col in range(0, width):
            rgb = pixels[pixel]
            # print(rgb)
            pixelGrid[col][row] = hex(rgb)
            pixel += 1

    for item in pixelGrid:
        open("output.c", "w")
        with open("output.c", "a") as file:
            file.write(mode0gstr.replace("!BMP_DATA!", str(pixelGrid).replace("[", "{").replace("]", "}").replace("'", "")))
            
def mode1():
    pixel = 0;
    # print(pixels)
    for row in range(0, height - 1):
        for col in range(0, width):
            rgb = pixels[pixel]
            # print(rgb)
            
            #RGB888 -> RGB332
            red = (int(rgb[0]) >> 5) << 5
            green = (int(rgb[1]) >> 5) << 2
            blue = (int(rgb[2]) >> 6)
            rgb = (red | green | blue)
            
            pixelGrid[col][row] = hex(rgb)
            pixel += 1

    for item in pixelGrid:
        open("output.c", "w")
        with open("output.c", "a") as file:
            file.write(mode1str.replace("!BMP_DATA!", str(pixelGrid).replace("[", "{").replace("]", "}").replace("'", "")))
            
def mode1g():
    pixel = 0;
    # print(pixels)
    for row in range(0, height - 1):
        for col in range(0, width):
            rgb = pixels[pixel]
            # print(rgb)
            
            pixelGrid[col][row] = hex(rgb)
            pixel += 1

    for item in pixelGrid:
        open("output.c", "w")
        with open("output.c", "a") as file:
            file.write(mode1gstr.replace("!BMP_DATA!", str(pixelGrid).replace("[", "{").replace("]", "}").replace("'", "")))
            
def mode2(): # 2 Pixels per uint_8t
    pixel = 0;
    pixel1 = 0b11110000; #4 bits per pixel in 8 bit integer
    # print(pixels)
    for row in range(0, height - 1):
        for col in range(0, width):
            rgb = pixels[pixel]
            
            #RGB888 -> RGB121
            red = (int(rgb[0]) >> 7) << 7
            green = (int(rgb[1]) >> 6) << 1
            blue = (int(rgb[2]) >> 7)
            rgb = (red | green | blue)
            
            if (col % 2 == 0):
                pixel1 = rgb << 4 #First of 2 pixels, move to front of uint_8t
            else:
                pixel = pixel1 | rgb #Last of 2 pixels, place in last 4 bits of uint_8t
                pixelGrid[col][row / 2] = hex(pixel)
            
for item in pixelGrid:
        open("output.c", "w")
        with open("output.c", "a") as file:
            file.write(mode2str.replace("!BMP_DATA!", str(pixelGrid).replace("[", "{").replace("]", "}").replace("'", "")))
            
if (mode == 0 and not greyscale):
    mode0()
elif (mode == 0 and greyscale):
    mode0g()
elif (mode == 1 and not greyscale):
    mode1()
elif (mode == 1 and greyscale):
    mode1g()
elif (mode == 2 and not greyscale):
    mode2()
