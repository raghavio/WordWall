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

def draw_words(draw, x, y, words):
    font = ImageFont.truetype("Quote.ttf", 56)

    word_1_size = draw.textsize(words[0], font) #Returns tuple (x, y)
    word_2_size = draw.textsize(words[1], font)

    word_1_x = (x - word_1_size[0]) / 2
    word_1_y = (y - word_1_size[1]) / 2 - y / 10

    word_2_x = (x - word_2_size[0]) / 2
    word_2_y = (y - word_2_size[1]) / 2 + y / 10

    draw.text((word_1_x, word_1_y), words[0], font=font)
    draw.text((word_2_x, word_2_y), words[1], font=font)
    words_data = (word_1_y, word_2_y, word_2_size[1])
    return words_data

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
    word_1_y, word_2_y, word_size_y = words_data

    font = ImageFont.truetype("LinLibertine_DR.ttf", 24)

    pronun_1_size = draw.textsize(pronunciations[0], font)
    pronun_2_size = draw.textsize(pronunciations[1], font)

    pronun_1_x = (x - pronun_1_size[0]) / 2
    pronun_1_y = (word_1_y - pronun_1_size[1])

    pronun_2_x = (x - pronun_2_size[0]) / 2
    pronun_2_y = (word_2_y + word_size_y)

    draw.text((pronun_1_x, pronun_1_y), pronunciations[0], font=font)
    draw.text((pronun_2_x, pronun_2_y), pronunciations[1], font=font)

    pronunciation_data = (pronun_1_y, pronun_2_y, pronun_2_size[1])
    return pronunciation_data

def draw_difinition(draw, x, y, pronun_data, synonyms_data):
    font_size = 28
    font = ImageFont.truetype("Quote.ttf", font_size)
    meaning_1 = "Remove the moisture from (something), typically in order to preserve it"
    example_1 = "a desiccated history of ideas"

    meaning_1_textsize = draw.textsize(meaning_1, font)
    example_1_textsize = draw.textsize(example_1, font)

    meaning_2 = "Remove the moisture from (something), typically in order to preserve it"
    example_2 = "a desiccated history of ideas"

    meaning_2_textsize = draw.textsize(meaning_1, font)
    example_2_textsize = draw.textsize(example_1, font)

    meaning_3 = "Remove the moisture from (something), typically in order to preserve it"
    example_3 = "a desiccated history of ideas"

    meaning_3_textsize = draw.textsize(meaning_1, font)
    example_3_textsize = draw.textsize(example_1, font)

    difinition_start_y = synonyms_data[0] + synonyms_data[2]
    difinition_end_y = pronun_data[0] - difinition_start_y
    print "start: ", difinition_start_y, " end: ", difinition_end_y, "mean size: ", meaning_1_textsize, "example size", example_1_textsize

    space = 10 #space between meaning and example in pixels

    meaning_1_x = (x - meaning_1_textsize[0]) / 2
    meaning_1_y = ((difinition_end_y - (meaning_1_textsize[1])) / 2) + difinition_start_y

    example_1_x = (x - example_1_textsize[0]) / 2
    example_1_y = ((difinition_end_y - example_1_textsize[1]) / 2) + difinition_start_y

    #draw.text((meaning_1_x, meaning_1_y), meaning_1, font=font)

    meaning_data = [meaning_1, meaning_2, meaning_3]
    example_data = [example_1, example_2, example_3]
    partition = difinition_end_y / 4
    for i in range(0, len(meaning_data)):
        '''
        meaning_size = draw.meaning_size(meaning_data[i], font)
        example_textsize = draw.textsize(example_data[i], font)
        while (meaning_size[y] + > x - (x / 15)): #Need to do for x as well
            font_size -= 1
            font = ImageFont.truetype("Quote.ttf", font_size)
            meaning_size = draw.textsize(meaning_data[i], font)
            example_textsize = draw.textsize(example_data[i], font)
        '''

        meaning_x = get_center_x(x, meaning_size[0])
        meaning_y = (difinition_start_y + (partition * (i + 1)) - meaning_size[1])# - meaning_size[1]/2
        example_y = (difinition_start_y + (partition * (i + 1)))# - meaning_size[1]/2
        draw.text((meaning_x, meaning_y), meaning_data[i], font=font)
        draw.text((meaning_x, example_y), example_data[i], font=font)

    #draw.text((meaning_1_x, example_1_y), example_1, font=font)
    #draw.point((x/2, 360), fill=(255,255,255,0))
    #draw.point((x/2, 540), fill=(255,255,255,0))
    #draw.point((x/2, y/5), fill=(255,255,255,0))

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

    synonyms_data = (synonyms_1_y, synonyms_2_y, synonyms_1_size[1])
    return synonyms_data

def get_dictionary_data(word):
    url = "http://www.oxforddictionaries.com/definition/english/" + word
    page = requests.get(url, verify=False).text
    soup = BeautifulSoup(page, "lxml")

    results = soup.select('section.se1 > h3.partOfSpeechTitle >\
                            span.partOfSpeech')[:3]
    part_of_speech = [result.text for result in results]

    count = len(part_of_speech)
    data = []
    for i in range(0, count):
        limit = 2 if count == 1 else 1
        results_1 = soup.select('div > section:nth-of-type('+str(i+1)+') \
                                    div.msDict.sense > div.senseInnerWrapper > \
                                    span.definition')[:limit]
        results_2 = soup.select('div > section:nth-of-type('+str(i+1)+') \
                                    div.msDict.sense > div.senseInnerWrapper > \
                                    span.exampleGroup > em.example')[:limit]
        for j in range(0, limit):
            data.append({'partOfSpeech' : part_of_speech[i],
                        'definition' : results_1[j].text,
                        'example' : results_2[j].text})
    return data

def get_synonyms(word):
    url = "http://www.thesaurus.com/browse/" + word
    page = requests.get(url, verify=False).text
    soup = BeautifulSoup(page, "lxml")
    synonyms = []

    result = soup.select('div#synonyms-0 > div.filters > \
                                    div.relevancy-block > div.relevancy-list > \
                                    ul > li > a > span.text')[:10]
    synonyms.extend([str(synonym.text.title()) for synonym in result])
    return synonyms

def main():
    get_dictionary_data('bird')
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
    words_data = draw_words(draw, x, y, words)
    if pronunciations is not None:
        pronun_data = draw_pronunciation(draw, x, y, pronunciations, words_data)
    synonyms_data = draw_synonyms(draw, x, y, synonyms_1, synonyms_2)
    draw_difinition(draw, x, y, pronun_data, synonyms_data)
    img.save('sample-out.jpg')

if __name__ == "__main__":
    main()
