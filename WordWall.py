#!/usr/bin/python
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup
from sys import platform

import requests
import os


def changeBackground(image_path):
    if platform == "darwin":
        import subprocess
        osx_script = """/usr/bin/osascript<<END
tell application "Finder"
set desktop picture to POSIX file "%s"
end tell
END"""
        subprocess.Popen(osx_script%image_path, shell=True)
        subprocess.call(['killall', 'Dock']) #To refresh the desktop
    elif platform == "linux" or platform == "linux2":
        None
    elif platform == "win32":
        None


def get_center_x(x, text_size_x):
    center_x = (x - text_size_x) / 2
    return center_x

def draw_definition(draw, x, y, definition_data, p_data, synonyms_data):
    font_name, font_size = "Definition.ttf", 28
    font_normal = ImageFont.truetype(font_name, font_size)

    definition_1_start_y = synonyms_data['synonyms_1_y'] + synonyms_data['synonyms_1_textsize_y']
    definition_1_end_y = p_data['pronun_1_y']
    definition_1_area_y = definition_1_end_y - definition_1_start_y

    definition_2_start_y = synonyms_data['synonyms_2_y']
    definition_2_end_y = p_data['pronun_2_y'] + p_data['pronun_2_textsize_y']
    definition_2_area_y = definition_2_start_y - definition_2_end_y

    length = [{'offset_y' : definition_1_start_y, 'area' : definition_1_area_y},
                {'offset_y' : definition_2_end_y, 'area' : definition_2_area_y}]
    draw_data = []
    for k in range(0, len(definition_data)): #Runs 2 times to display definition(s) of 2 words
        define_count = len(definition_data[k])
        if define_count == 0: #If no definition found for word
            continue
        partition = length[k]['area'] / (define_count+1)
        for i in range(0, define_count):
            definition = definition_data[k][i][1]['definition']
            example = definition_data[k][i][1]['example']
            num_bullet = definition_data[k][i][1]['num_bullet']
            meaning_size = draw.textsize(definition, font_normal)
            example_size = draw.textsize(example, font_normal) if example != None else (0, 0)
            num_bullet_size = draw.textsize(num_bullet, font_normal)

            border = x - (x / 15)
            # or ((meaning_size[1] + example_size[1]) * define_count) > length[k]['area'] - (length[k]['area']/2.7)
            while (meaning_size[0] > border or example_size[0] > border): #Need to do for y as well?
                font_size -= 1
                font_normal = ImageFont.truetype(font_name, font_size)
                meaning_size = draw.textsize(definition, font_normal)
                example_size = draw.textsize(example, font_normal) if example != None else (0, 0)

            meaning_x = get_center_x(x, meaning_size[0])
            meaning_y = (length[k]['offset_y'] + (partition * (i + 1)) - (meaning_size[1] if example != None else 0))# - meaning_size[1]/2
            example_x = get_center_x(x, example_size[0])
            example_y = (length[k]['offset_y'] + (partition * (i + 1)))# - meaning_size[1]/2

            draw_data.append({'meaning_x' : meaning_x, 'meaning_y' : meaning_y,
                                'example_x' : example_x,'example_y' : example_y,
                                'definition' : definition, 'example' : example,
                                'font' : font_normal,
                                'partOfSpeech' : definition_data[k][i][0],
                                'num_bullet_size_x' : num_bullet_size[0]})
            font_size = 28
            font_normal = ImageFont.truetype(font_name, font_size)
    min_x = min(min([(content['meaning_x'], content['example_x']) for content in draw_data]))
    for i, content in enumerate(draw_data):
        example = content['example']
        meaning_y = content['meaning_y']

        draw.text((min_x, content['meaning_y']), content['definition'], font=content['font'])
        if example != None:
            draw.text((content['num_bullet_size_x'] + min_x, content['example_y']), example, font=content['font'])

def get_dictionary_data(words):
    data = []
    pronunciation_data = []
    for word in words:
        url = "http://www.oxforddictionaries.com/definition/english/" + word
        while True:
            try:
                page = requests.get(url, timeout=5).text
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print "ConnectionError occured in get_dictionary_data()"
                pass
        soup = BeautifulSoup(page, "lxml")

        results = soup.select('section.se1 > h2.partOfSpeechTitle >\
                                span.partOfSpeech')[:3]
        part_of_speech = [result.text for result in results]
        pronun_result_raw = soup.find("div", class_="headpron")
        pronunciation = "" if pronun_result_raw is None else\
                        pronun_result_raw.find(text=True, recursive=False)\
                            .replace('/','[', 1).replace('/', ']', 1).strip()
        pronunciation_data.append(pronunciation)
        count = len(part_of_speech)
        definition_data = []
        for i in range(0, count):
            limit = 2 if count == 1 else 1
            results_1_raw = soup.select('div > section:nth-of-type('+str(i+1)+') \
                                        div.msDict.sense > div.senseInnerWrapper > \
                                        span.definition')[:limit]
            if not results_1_raw: #If there's no definition, no point going further
                continue
            for j, definition in enumerate(results_1_raw):
                results_2_raw = results_1_raw[j].parent.select("span.exampleGroup.exGrBreak \
                                                                > em.example")
                example = None if not results_2_raw else '"'+results_2_raw[0].text+'"'
                num_bullet = str(j+1)+".  " if limit == 2 else "1.  "

                dictionary = {'definition' : num_bullet + definition.text.strip(),
                                'example' : example, 'num_bullet' : num_bullet}
                definition_data.append([part_of_speech[i], dictionary])
        data.append(definition_data)
    return data, pronunciation_data

def draw_pronunciation(draw, x, y, pronunciations, words_data):
    word_1_y, word_2_y, word_size_y = words_data

    font = ImageFont.truetype("Pronunciation.ttf", 22)

    pronun_1_size = draw.textsize(pronunciations[0], font)
    pronun_2_size = draw.textsize(pronunciations[1], font)

    space = 5
    pronun_1_x = get_center_x(x, pronun_1_size[0])
    pronun_1_y = (word_1_y - pronun_1_size[1] - space)

    pronun_2_x = get_center_x(x, pronun_2_size[0])
    pronun_2_y = (word_2_y + word_size_y + space)

    draw.text((pronun_1_x, pronun_1_y), pronunciations[0], font=font)
    draw.text((pronun_2_x, pronun_2_y), pronunciations[1], font=font)

    pronunciation_data = {'pronun_1_y' : pronun_1_y, 'pronun_2_y' : pronun_2_y,
                            'pronun_2_textsize_y' : pronun_2_size[1]}
    return pronunciation_data

def draw_words(draw, x, y, words):
    font = ImageFont.truetype("Words.ttf", 56)

    word_1_size = draw.textsize(words[0], font) #Returns tuple (x, y)
    word_2_size = draw.textsize(words[1], font)

    word_1_x = get_center_x(x, word_1_size[0])
    word_1_y = (y - word_1_size[1]) / 2 - y / 13

    word_2_x = get_center_x(x, word_2_size[0])
    word_2_y = (y - word_2_size[1]) / 2 + y / 13

    draw.text((word_1_x, word_1_y), words[0], font=font)
    draw.text((word_2_x, word_2_y), words[1], font=font)
    words_data = (word_1_y, word_2_y, word_2_size[1])
    return words_data

def get_words():
    url = "http://www.vocabulary.com/dictionary/randomword"
    words = []

    for x in range(0, 2):
        while True:
            try:
                page = requests.get(url, timeout=5).text
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print "ConnectionError occured in get_words()"
                pass
        soup = BeautifulSoup(page, "lxml")
        word = str(soup.select('div.wordPage')[0]['data-word']).upper()
        words.append(word)

    return words

def draw_synonyms(draw, x, y, synonyms_1, synonyms_2): #To be scaled
    synonyms_1 = "Synonyms: " + ', '.join(synonyms_1)
    synonyms_2 = "Synonyms: " + ', '.join(synonyms_2)
    font = ImageFont.truetype("Quote.ttf", 24)
    synonyms_1_size = draw.textsize(synonyms_1, font)
    synonyms_1_x = get_center_x(x, synonyms_1_size[0])
    synonyms_1_y = y / 13

    synonyms_2_size = draw.textsize(synonyms_2, font)
    synonyms_2_x = get_center_x(x, synonyms_2_size[0])
    synonyms_2_y = y - (y / 13) - synonyms_2_size[1]

    draw.text((synonyms_1_x, synonyms_1_y), synonyms_1, font=font)
    draw.text((synonyms_2_x, synonyms_2_y), synonyms_2, font=font)

    synonyms_data = {'synonyms_1_y' : synonyms_1_y, 'synonyms_2_y': synonyms_2_y,
                        'synonyms_1_textsize_y' : synonyms_1_size[1]}
    return synonyms_data

def get_synonyms(word):
    url = "http://www.thesaurus.com/browse/" + word
    while True:
        try:
            page = requests.get(url, timeout=5).text
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print "ConnectionError occured in get_synonyms()"
            pass
    soup = BeautifulSoup(page, "lxml")
    synonyms = []

    result = soup.select('div#synonyms-0 > div.filters > \
                                    div.relevancy-block > div.relevancy-list > \
                                    ul > li > a > span.text')[:10]
    synonyms.extend([synonym.text.title().encode('utf-8') for synonym in result])
    return synonyms

def draw_quote(draw, x, y, quote, author):
    font_size = 24
    font = ImageFont.truetype("Quote.ttf", font_size)
    quote_size = draw.textsize(quote, font)
    while (quote_size[0] > x - (x / 15)):
        font_size -= 1
        font = ImageFont.truetype("Quote.ttf", font_size)
        quote_size = draw.textsize(quote, font)

    author_size = draw.textsize(author, font)
    center_x_quote = get_center_x(x, quote_size[0])
    center_y_quote = (y - (quote_size[1] + author_size[1])) / 2
    draw.text((center_x_quote, center_y_quote), quote, font=font)

    center_x_author = get_center_x(x, author_size[0])
    center_y_author = center_y_quote + quote_size[1]
    draw.text((center_x_author, center_y_author), author, font=font)

def get_quote():
    api_url = "http://api.theysaidso.com/qod"
    default_quote = '"Don\'t cry because it\'s over, smile because it happened."'
    default_quote_author = 'Dr. Seuss'
    while True:
        try:
            json = requests.get(api_url, timeout=5).json()
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print "ConnectionError occured in get_quote()"
            pass
    content = json.get('contents')

    if content is not None:
        quote = content['quotes'][0]['quote']
        author = content['quotes'][0]['author']

        return quote, author
    else:
        return default_quote, default_quote_author

def main():
    img = Image.open("background.jpg")
    img.thumbnail((1440,900))

    draw = ImageDraw.Draw(img)
    x, y = img.size

    words = get_words()
    print words[0], words[1]

    quote, author = get_quote()
    draw_quote(draw, x, y, quote, author)

    synonyms_1 = get_synonyms(words[0])
    synonyms_2 = get_synonyms(words[1])
    synonyms_data = draw_synonyms(draw, x, y, synonyms_1, synonyms_2)

    words_data = draw_words(draw, x, y, words)

    data, pronunciations = get_dictionary_data(words)

    p_data = draw_pronunciation(draw, x, y, pronunciations, words_data)
    draw_definition(draw, x, y, data, p_data, synonyms_data)

    new_image_name = "wordwall.jpg"
    img.save(new_image_name)
    image_path = os.path.abspath(new_image_name)
    changeBackground(image_path)

if __name__ == "__main__":
    main()
