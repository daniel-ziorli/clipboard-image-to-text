import random
from easyocr import Reader
from PIL import ImageGrab, ImageEnhance, Image
import keyboard
import os
import json
from textblob import Word
import cv2
import numpy as np

def get_bounding_box_key(input):
    box = input[0]
    
    x = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
    y = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
    
    return x + y * 1000

def sort_bounding_boxes(bounding_boxes):
    sorted_boxes = sorted(bounding_boxes, key= lambda x:get_bounding_box_key(x))
    return sorted_boxes

def get_left_most_value(input):
    
    left_most_value = 999
    for box, _, _ in input:
        min_x = min(box[0][0], box[1][0], box[2][0], box[3][0])
        if min_x < left_most_value:
            left_most_value = min_x
            
    return left_most_value
    
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
    
def get_leftmost_point(bounding_boxes):
    leftmost_point = None

    for box_info in bounding_boxes:
        bounding_box, _, _ = box_info
        for point in bounding_box:
            if leftmost_point is None or point[0] < leftmost_point[0]:
                leftmost_point = point

    return leftmost_point

def generate_text_from_ocr(results):
    output = ''
    prev_y_max = -1
    # y_padding = 40
    # x_padding = 20
    y_padding = 0
    x_padding = 0
    
    
    if len(results) == 0:
        return ''

    # sorted_results = sort_bounding_boxes(results)
    char_width = get_average_char_width(results)
    left_line = get_left_most_value(results)
    
    draw_bb(results)

    for box, text, _ in results:
        y_max = max(box[0][1], box[1][1], box[2][1], box[3][1])

        if y_max > prev_y_max + y_padding and prev_y_max != -1:
            output = output[:-1]
            output += '\n'
            
        if len(output) != 0 and output[-1] == '\n':
            x_min = min(box[0][0], box[1][0], box[2][0], box[3][0])
            spaces = ((x_min + x_padding) - left_line) // char_width
            output += ' ' * int(spaces)
            
        output += text + ' '
        prev_y_max = y_max
        
    output = output[:-1]
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