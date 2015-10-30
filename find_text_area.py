from PIL import Image
import pyscreenshot as screenshot_maker
from fingerbot import read
import pyautogui as gui
from time import sleep


class ColorFound(Exception):
    pass


_ = raw_input('Press enter to start...')

language_button_color = (92, 184, 92)
white_table_color = (255, 255, 255)
bg_color = (189, 222, 255)
edge_colors = {(189, 222, 249), (152, 189, 220), (187, 224, 255), (181, 218, 249), (187, 223, 255), (142, 182, 216),
               (172, 202, 229), (148, 186, 218), (171, 201, 227), (243, 248, 251), (189, 222, 251), (182, 218, 249),
               (202, 221, 237), (181, 217, 249)}


def get_screen():
    I = screenshot_maker.grab().save('/tmp/grabbed.png')
    I = Image.open(open('/tmp/grabbed.png'))
    return I
    # I = Image.open('/tmp/grabbed.png')


def get_coordinates(img):
    def get_language_button(matrix, width, height):

        try:
            for hp in range(height)[::5]:
                for wp in range(width)[::5]:
                    r, g, b = matrix[wp, hp]
                    # print(hp, wp, r,g,b)
                    if (r, g, b) == language_button_color:
                        button_height = hp
                        button_width = wp
                        raise ColorFound()
        except ColorFound:
            print("Found the color at [{}, {}] - going down!".format(wp, hp))
            return button_width, button_height
            # TODO: else fail - not found

    def get_text_box_upper(matrix, language_button_coords, width, height):
        try:
            for hp in range(language_button_coords[1], height)[::5]:
                r, g, b = matrix[language_button_coords[0], hp]
                if (r, g, b) == white_table_color:
                    left_corner_width = language_button_coords[0]
                    left_corner_height = hp
                    raise ColorFound()
        except ColorFound:
            print("Found the table at [{}, {}] - going right!".format(language_button_coords[1], hp))
            return left_corner_width, left_corner_height
            # TODO: else fail - not found

    def get_text_box_right(matrix, upper_coords, width, height):
        try:
            for wp in range(upper_coords[0], width)[::5]:
                r, g, b = matrix[wp, upper_coords[1]]
                if (r, g, b) != white_table_color and (r, g, b) in edge_colors:
                    right_corner_width = wp - 5
                    right_corner_height = upper_coords[1]
                    raise ColorFound()
        except ColorFound:
            print(
            "Found the right end of table at [{}, {}] - going down!".format(right_corner_width, right_corner_height))
            return right_corner_width, right_corner_height

    def get_text_box_lower(matrix, right_coords, width, height):
        try:
            for hp in range(right_coords[1], height):
                r, g, b = matrix[right_coords[0], hp]
                if (r, g, b) != white_table_color:
                    lower_right_height = hp - 5
                    lower_right_width = right_coords[0]
                    raise ColorFound()
        except ColorFound:
            print("Found the lower right end of table at [{}, {}]".format(lower_right_width, lower_right_height))
            return lower_right_width, lower_right_height

    def get_entry_box(matrix, left_corner_width, right_corner_width, lower_right_height, width, height):
        middle_of_text_box_width = left_corner_width + (right_corner_width - left_corner_width) // 2
        # print(middle_of_text_box_width)

        look_for_white = False
        try:
            for hp in range(lower_right_height, height)[::3]:
                r, g, b = matrix[middle_of_text_box_width, hp]
                # print("looking at [{}, {}]".format(middle_of_text_box_width, hp))
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
            return entry_mid_width, entry_mid_height

    matrix = img.load()
    width, height = img.size

    d = {"crop": {"up-left": [], "low-right": []}, "entry": []}

    button = get_language_button(matrix, width, height)
    if not button:
        return False
    upper = get_text_box_upper(matrix, button, width, height)
    if not upper:
        return False
    right = get_text_box_right(matrix, upper, width, height)
    if not right:
        return False
    lower = get_text_box_lower(matrix, right, width, height)
    if not lower:
        return False
    entry = get_entry_box(matrix, upper[0], right[0], lower[1], width, height)
    if not entry:
        return False

    d["crop"]["up-left"] = upper
    d["crop"]["low-right"] = lower
    d['entry'] = entry

    return d

def words_to_wpm_rate(words, wpm):
    total = sum([len(w)+1 for w in words])
    avg_char = float(total) / len(words)
    per_second = wpm / 60.
    speed = 1./per_second/avg_char
    return speed

first_run = True
while True:
    grab = get_screen()
    coordinates = get_coordinates(grab)
    print(coordinates)
    if coordinates:
        cropped = grab.crop((coordinates["crop"]["up-left"][0],
                             coordinates["crop"]["up-left"][1],
                             coordinates["crop"]["low-right"][0],
                             coordinates["crop"]["low-right"][1]))
        cropped.save('/tmp/grabbed_cropped.png')
        words = read(cropped)
        if first_run:
            gui.moveTo(coordinates["entry"][0], coordinates["entry"][1], duration=1)
            gui.click()
            sleep(1)
            first_run = False
        print(" ".join(words))
        speed = words_to_wpm_rate(words, 250)
        print("going at speed: {}".format(speed))
        for word in words:
            gui.typewrite(word + ' ', interval=speed)
    else:
        exit(0)
