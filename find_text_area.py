from PIL import Image
import pyscreenshot as screenshot_maker

class ColorFound(Exception):
    pass

_ = raw_input('Press enter to start...')
I = screenshot_maker.grab().save('/tmp/grabbed.png')
I = Image.open('/tmp/grabbed.png')
# 92, 184, 92
language_button_color = (92, 184, 92)
white_table_color = (255, 255, 255)
bg_color = (189, 222, 255)
print(type(I))
pix_array = I.load()
width, heigth = I.size

# find the language button
print(width, heigth)
def get_coordinates(img):
try:
    for hp in range(heigth)[::5]:
        for wp in range(width)[::5]:
            r, g, b = pix_array[wp, hp]
            print(hp, wp, r,g,b)
            if (r, g, b) == language_button_color:
                button_height = hp
                button_width = wp
                raise ColorFound()
except ColorFound:
    print("Found the color at [{}, {}] - going down!".format(wp, hp))
# TODO: else fail - not found

# go down and find the upper edge of text box
try:
    for hp in range(button_height, heigth)[::5]:
        r, g, b = pix_array[button_width, hp]
        if (r, g, b) == white_table_color:
            left_corner_width = button_width
            left_corner_height = hp
            raise ColorFound()
except ColorFound:
    print("Found the table at [{}, {}] - going right!".format(button_width, hp))
    point1 = (left_corner_width, left_corner_height)
# TODO: else fail - not found

# go right and find the right edge of text box
try:
    for wp in range(left_corner_width, width)[::5]:
        r, g, b = pix_array[wp, left_corner_height]
        if (r, g, b) != white_table_color:
            right_corner_width = wp - 5
            right_corner_height = left_corner_height
            raise ColorFound()
except ColorFound:
    print("Found the right end of table at [{}, {}] - going down!".format(right_corner_width, right_corner_height))

# go down and find the lower edge of text box
try:
    for hp in range(right_corner_height, heigth):
        r, g, b = pix_array[right_corner_width, hp]
        if (r, g, b) != white_table_color:
            lower_right_height = hp - 5
            lower_right_width = right_corner_width
            raise ColorFound()
except ColorFound:
    print("Found the lower right end of table at [{}, {}]".format(lower_right_width, lower_right_height))

# go down from the middle of the text box and find the entry box
middle_of_text_box_width = left_corner_width + ( right_corner_width - left_corner_width) // 2
print(middle_of_text_box_width)

look_for_white = False
try:
    for hp in range(lower_right_height, heigth)[::3]:
        r, g, b = pix_array[middle_of_text_box_width, hp]
        print("looking at [{}, {}]".format(middle_of_text_box_width, hp))
        if look_for_white:
            if (r, g, b) == white_table_color:
                entry_mid_width = middle_of_text_box_width
                entry_mid_height = hp
                text_box_xy = (entry_mid_width, entry_mid_height)
                raise ColorFound()
        if (r, g, b) != bg_color:
            continue
        look_for_white = True
except:
    print("Found the lower right end of table at [{}, {}]".format(entry_mid_width, entry_mid_height))




cropped = I.crop((left_corner_width, left_corner_height, lower_right_width, lower_right_height))
cropped.save('/tmp/test1.png')
from fingerbot import read
words = read(cropped)

import pyautogui as gui
gui.moveTo(text_box_xy[0], text_box_xy[1], duration=1)
gui.click()
from time import sleep
sleep(1)
for word in words:
    gui.typewrite(word+' ', interval=0.1)
