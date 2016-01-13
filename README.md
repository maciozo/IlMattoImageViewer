# Bitmap image viewer for the Il Matto

![^?^](http://puu.sh/muIip/2df850fa11.jpg)

This script generates a C source file that when compiled and flashed on the the Il Matto, displays a single image on the display.

### Dependencies
* Python 3.4 (Untested on other versions)
* Pillow
* lcdlib
* avr-gcc
* avrdude (or other suitable tool)

### Usage
1. Find an image, RGB888, 4:3 aspect ratio for best results.
2. Edit variables `mode`, `rotateAngle`, `greyscale`, and `im`.
3. Run `python bmp2matto.py`
4. Build `output.c` with `avr-gcc -DF_CPU=12000000 -mmcu=atmega644p -Wall -Os output.c -o output.elf -Wl,liblcd.a`
5. Convert binary to hex `avr-objcopy -O ihex output.elf output.hex`
6. Flash to Il Matto `avrdude -c usbasp -p m644p -U flash:w:output.hex`

### Image formats
No compression or complex image scaling has been implemented, so the image formats are limited to:
* 30x40x16 in RGB565 or greyscale
* 48x64x8 in RGB332 or greyscale
* 60x80x4 in RGB121 or greyscale (not yet implemented)
* 120x160x2 in greyscale (not yet implemented)