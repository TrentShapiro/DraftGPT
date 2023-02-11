import json
import re
import subprocess

import cv2
import numpy as np
import pytesseract
import requests
from PIL import ImageGrab


def process_text(text, replacement, verbose = False):
    if verbose:
        print(repr(text))
    text = re.sub(r"[^\w\s,]", replacement, text)
    try:
        text = re.findall("[a-z A-z]{2,}", text)[0].strip()
    except:
        text = text
    if verbose:
        print(repr(text))
    return text


def text_from_box(image, start_x, end_x, start_y, end_y):
    perturbations = [
        [0, 0],
        [0, 1], [1, 0], [ 1, 1],
        [-1,0], [0,-1], [-1,-1],
        [-1,1], [1,-1]
    ]
    
    for d in perturbations:
        box_img = image[start_y+d[1]:end_y+d[1],start_x+d[0]:end_x+d[0]]
        text = pytesseract.image_to_string(box_img)
        if text != '':
            return text

    return ''


def find_text_box(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret,thresh = cv2.threshold(gray,50,255,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)

    cards = []
    for cnt in contours:
        x1,y1 = cnt[0][0]
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            ratio = float(w)/h
            if ratio >= 0.9 and ratio <= 1.1:
                continue
            else:
                if (w>200) and (h>200) and (w<500) and (h<500):
                    cv2.putText(img, 'Card', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                    img = cv2.drawContours(img, [cnt], -1, (0,255,0), 1)
                    cards.append(cnt)


    corners = []
    for card in cards:
        min_x = min([point[0][0] for point in card])
        max_x = max([point[0][0] for point in card])
        min_y = min([point[0][1] for point in card])
        max_y = max([point[0][1] for point in card])
        corners.append([(min_x, min_y),(max_x,max_y)])

    text_values = []
    for rect in corners:
        start_x = rect[0][0] + 16
        start_y = rect[0][1] + 16
        end_x = start_x + 140
        end_y = start_y + 14
        cv2.rectangle(img, (start_x,start_y),(end_x,end_y),(0,0,255),1)
        text = text_from_box(img, start_x,end_x,start_y,end_y)
        text = process_text(text,'')
        text_values.append(text)
        cv2.putText(img, text, (start_x, start_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 1)


    return img, corners, text_values


def get_scryfall_info(raw_card_name):
    url_base = 'https://api.scryfall.com/cards/named?fuzzy='
    query_url = url_base + raw_card_name.replace(' ','%20')

    card_info = requests.get(query_url)

    if card_info.status_code == 404:
        return None # f'Could not find {raw_card_name}'

    try:
        card_text = json.loads(card_info.text)
        name = card_text['name']
        type_line = card_text['type_line']
        mana_cost = '\n'+card_text['mana_cost'] if card_text['mana_cost'] != '' else False
        rarity = card_text['rarity']
        oracle_text = card_text['oracle_text']
        stat_line = False
        if 'Creature' in type_line:
            power = card_text['power']
            toughness = card_text['toughness']
            stat_line = f'\n{power}/{toughness}'

        return f'''
{name}
{type_line}{mana_cost if mana_cost else ''}
{rarity}{stat_line if stat_line else ''}
{oracle_text}
'''
    except:
        return None # f'Could not parse json for {raw_card_name}'


coords = subprocess.Popen(
    ['python','external/select_bounding_box.py'],
    stdout=subprocess.PIPE).communicate()[0]

coords = coords.decode().strip()
x1,y1,x2,y2 = [int(i) for i in coords.split(' ')]

raw_cardnames = []
while True:
    window_selection = ImageGrab.grab(bbox=(x1,y1,x2,y2))
    img = np.array(window_selection)

    img, corners, text_values = find_text_box(img)

    # Update raw strings to reduce duplicate calls
    raw_cardnames += [i for i in text_values if i not in raw_cardnames]

    cv2.imshow("draft", img)

    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break

raw_cardnames = list(set(raw_cardnames))
print(raw_cardnames)
new_cardname_lookup = [
    get_scryfall_info(i) for i in raw_cardnames
]

for entry in new_cardname_lookup:
    if entry is not None:
        print(entry)