from easyocr import Reader
from PIL import ImageGrab, ImageEnhance, Image
import keyboard
import os
import json
from textblob import Word
import numpy as np
from utils import get_clipboard_img, generate_text_from_ocr

def paste_clipboard_image_text():
    path = 'temp-clipboard-image-to-text.png'
    img = get_clipboard_img(path)
    if img == None:
        return

    results = reader.readtext(path, width_ths=10, height_ths=1)
    
    output = generate_text_from_ocr(results)
    
    keyboard.write(output)
    # os.remove(path)

if not os.path.isfile('config.json'):
    default_config = '{"language": "en","clipboard-image-to-text-hotkey": "ctrl+shift+v"}'
    json_object = json.loads(default_config)
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

reader = Reader([config['language']], gpu=config['use_gpu'])

keyboard.add_hotkey(config['clipboard-image-to-text-hotkey'], lambda: paste_clipboard_image_text())
keyboard.wait()
