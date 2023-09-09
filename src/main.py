import cv2
import keyboard
import os
import json
from utils import get_clipboard_img, generate_text_from_ocr, read_config
from paddleocr import PaddleOCR

def paste_clipboard_image_text():
    path = 'temp-clipboard-image-to-text.png'
    img = get_clipboard_img(path)
    if img == None:
        return
    
    cv2_img = cv2.imread(path)

    results = reader.ocr(cv2_img)[0]
    output = generate_text_from_ocr(results)

    keyboard.write(output)

if not os.path.isfile('config.json'):
    default_config = '{"language": "en","clipboard-image-to-text-hotkey": "ctrl+shift+v","use_gpu": true,"auto_correct": false, "new_line_detection_padding": 2,"new_line_character": "\r\n"}'
    json_object = json.loads(default_config)
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

reader = PaddleOCR(lang='en', use_angle_cls=True, show_log=False, use_gpu=True)
keyboard.add_hotkey(config['clipboard-image-to-text-hotkey'], lambda: paste_clipboard_image_text())
keyboard.wait()
