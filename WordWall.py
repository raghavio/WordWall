from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup

from wordnik import *

import requests

def get_center_x(x, text_size_x):
    center_x = (x - text_size_x) / 2
    return center_x

def get_center_y(y, text_size_y):
    center_y = (y - text_size_y) / 2
    return center_y

def get_left_x(x, text_size):
    left_x = x/4 - text_size[0]/2
    return left_x

def get_left_y(y, text_size):
    left_y = (y - text_size[1]) / 2
    return left_y

def get_right_x(x, text_size):
    #center + left
    right_x = (x - get_left_x(x, text_size)) - text_size[0]
    return right_x

def get_right_y(y, text_size):
    #center + left
    right_y = get_center_y(y, text_size)
    return right_y

def draw_center(draw, x, y, text, font):
    text_size = draw.textsize(text, font)
    center_x = get_center_x(x, text_size)
    center_y = get_center_y(y, text_size)

    draw.text((center_x, center_y), text, font=font)

def draw_left(draw, x, y, text, font):
    text_size = draw.textsize(text, font)
    left_x = get_left_x(x, text_size)
    left_y = get_left_y(y, text_size)

    draw.text((left_x, left_y), text, font=font)

def draw_right(draw, x, y, text, font):
    text_size = draw.textsize(text, font)
    right_x = get_right_x(x, text_size)
    right_y = get_right_y(y, text_size)

    draw.text((right_x, right_y), text, font=font)

def draw_words(draw, x, y, words, pronunciations):
    font = ImageFont.truetype("Quote.ttf", 56)

    word_1_size = draw.textsize(words[0], font) #Returns tuple (x, y)
    word_2_size = draw.textsize(words[1], font)

    word_1_x = (x - word_1_size[0]) / 2
    word_1_y = (y - word_1_size[1]) / 2 - y / 10

    word_2_x = (x - word_2_size[0]) / 2
    word_2_y = (y - word_2_size[1]) / 2 + y / 10
    if pronunciations is not None:
        words_data = (word_1_y, word_2_y, word_2_size)
        draw_pronunciation(draw, x, y, pronunciations, words_data)
    draw.text((word_1_x, word_1_y), words[0], font=font)
    draw.text((word_2_x, word_2_y), words[1], font=font)

def draw_quote(draw, x, y, quote, author):
    font_size = 24
    font = ImageFont.truetype("Quote.ttf", font_size)
    quote_size = draw.textsize(quote, font)
    while (quote_size[0] > x - (x / 15)):
        font_size -= 1
        font = ImageFont.truetype("Quote.ttf", font_size)
        quote_size = draw.textsize(quote, font)
    author_size = draw.textsize(author, font)
    center_x = get_center_x(x, quote_size[0])
    center_y = get_center_y(y, quote_size[1]+author_size[1])
    draw.text((center_x, center_y), quote, font=font)
    draw.text((get_center_x(x, author_size[0]), center_y + quote_size[1]), author, font=font)

def draw_pronunciation(draw, x, y, pronunciations, words_data):
    word_1_y, word_2_y, word_2_size = words_data

    font = ImageFont.truetype("LinLibertine_DR.ttf", 24)

    pronun_1_size = draw.textsize(pronunciations[0], font)
    pronun_2_size = draw.textsize(pronunciations[1], font)

    pronun_1_x = (x - pronun_1_size[0]) / 2
    pronun_1_y = (word_1_y - pronun_1_size[1])

    pronun_2_x = (x - pronun_2_size[0]) / 2
    pronun_2_y = (word_2_y + word_2_size[1])

    draw.text((pronun_1_x, pronun_1_y), pronunciations[0], font=font)
    draw.text((pronun_2_x, pronun_2_y), pronunciations[1], font=font)

def draw_synonyms(draw, x, y, synonyms_1, synonyms_2):
    synonyms_1 = "Synonyms: " + ', '.join(synonyms_1)
    synonyms_2 = "Synonyms: " + ', '.join(synonyms_2)
    font = ImageFont.truetype("Quote.ttf", 24)
    synonyms_1_size = draw.textsize(synonyms_1, font)
    synonyms_1_x = get_center_x(x, synonyms_1_size[0])
    synonyms_1_y = y / 15

    synonyms_2_size = draw.textsize(synonyms_2, font)
    synonyms_2_x = get_center_x(x, synonyms_2_size[0])
    synonyms_2_y = y - (y / 15) - synonyms_2_size[1]

    draw.text((synonyms_1_x, synonyms_1_y), synonyms_1, font=font)
    draw.text((synonyms_2_x, synonyms_2_y), synonyms_2, font=font)

def get_synonyms(word):
    url = "http://www.thesaurus.com/browse/" + word
    page = requests.get(url, verify=False, timeout=5).text
    soup = BeautifulSoup(page, "lxml")
    synonyms = []

    result = soup.select('div#synonyms-0 > div.filters > \
                                    div.relevancy-block > div.relevancy-list > \
                                    ul > li > a > span.text')[:10]
    synonyms.extend([str(synonym.text.title()) for synonym in result])
    return synonyms

def main():

    apiUrl = 'http://api.wordnik.com/v4'
    apiKey = 'e110a032e7d3b2839b30a00f59f0e7d6e6cf459f5ec60f9cc'
    client = swagger.ApiClient(apiKey, apiUrl)
    wordApi = WordApi.WordApi(client)

    words = []

    url = "http://www.vocabulary.com/dictionary/randomword"
    for x in range(0, 2):
        page = requests.get(url, verify=False, timeout=5).text
        soup = BeautifulSoup(page, "lxml")
        word = str(soup.select('div.wordPage')[0]['data-word']).title()
        words.append(word)

    img = Image.open("image.jpg")
    img = img.crop((0,0,1440,900))
    draw = ImageDraw.Draw(img)

    x, y = img.size

    quote = '"Don\'t cry because it\'s over, smile because it happened."'
    author = "Some wise guy"
    pronunciations = ["[kwid-nuhngk]", "[Pro-nun-ci-at-ion]"]
    synonyms_1 = get_synonyms(words[0]) #Returns list of words
    synonyms_2 = get_synonyms(words[1])


    draw_quote(draw, x, y, quote, author)
    draw_words(draw, x, y, words, pronunciations)
    draw_synonyms(draw, x, y, synonyms_1, synonyms_2)
    img.save('sample-out.jpg')
    print img.size

if __name__ == "__main__":
    main()
