import random
from easyocr import Reader
from PIL import ImageGrab, ImageEnhance, Image
import keyboard
import os
import json
from textblob import TextBlob
import cv2
import numpy as np
    
def get_clipboard_img(path):
    img = ImageGrab.grabclipboard()
    if img == None:
        return None

    img.save(path,'PNG')
    
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    
    img = cv2.resize(img, None, fx=4, fy=4)

    # Calculate the average pixel intensity of the image
    avg_pixel_intensity = np.mean(img)

    # Determine the background color (white or black) based on the average pixel intensity
    if avg_pixel_intensity > 127:
        # For predominantly white background, use regular thresholding
        _, threshed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    else:
        # For predominantly black background, use inverted thresholding
        _, threshed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    cv2.imwrite(path, threshed)

    return True

def get_bounding_box_width(bounding_box):
    x_coordinates = [point[0] for point in bounding_box]
    return max(x_coordinates) - min(x_coordinates)

def get_left_most_value(input):
    
    left_most_value = 999
    for box, _, _ in input:
        min_x = min(box[0][0], box[1][0], box[2][0], box[3][0])
        if min_x < left_most_value:
            left_most_value = min_x
            
    return left_most_value

def get_average_char_width(results):
    if len(results) == 0:
        return -1
    character_width_sum = 0
    for box, text, _ in results:
        width = get_bounding_box_width(box)
        text_length = len(text)
        char_width = width // text_length
        character_width_sum += char_width
        
    return character_width_sum // len(results)

def generate_text_from_ocr(results, auto_correct = False):
    output = ''
    prev_y_max = -1
    y_padding = 0
    x_padding = 0
    
    
    if len(results) == 0:
        return ''

    char_width = get_average_char_width(results)
    line_height = get_average_char_width(results)
    
    left_line = get_left_most_value(results)
    
    draw_bb(results)

    for box, text, _ in results:
        y_max = max(box[0][1], box[1][1], box[2][1], box[3][1])
        

        if y_max > prev_y_max and prev_y_max != -1:
            output = output[:-1]
            y_min = min(box[0][1], box[1][1], box[2][1], box[3][1])
            height = y_max - y_min
            new_lines = (y_max - prev_y_max) // height
            output += '\n' * new_lines
            
        if len(output) != 0 and output[-1] == '\n':
            x_min = min(box[0][0], box[1][0], box[2][0], box[3][0])
            spaces = (x_min - left_line) // char_width
            output += ' ' * int(spaces)
            
        output += text + ' '
        prev_y_max = y_max
        
    output = output[:-1]
    
    if auto_correct:
        blob = TextBlob(output)
        corrected_output = blob.correct()
        return corrected_output
    
    return output

def draw_bb(input):
    image = cv2.imread('temp-clipboard-image-to-text.png')
    i = 0
    for box, text, _ in input:
        (tl, tr, br, bl) = box
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        cv2.rectangle(image, tl, br, (0, 255, 0), 2)
        cv2.putText(image, text, (tl[0], tl[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(image, str(i), (tr[0] - 20, tr[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        i += 1
        
    cv2.imwrite('temp-clipboard-image-to-text.png', image)
