from PIL import Image
import sys

import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
tool = tools[0]
builder = pyocr.builders.TextBuilder()

def read(img):
    lang = 'eng'
    txt = tool.image_to_string(img, lang=lang, builder=builder)
    words = txt.split()
    return words


