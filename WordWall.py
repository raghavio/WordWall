from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup

import requests

def get_center_x(x, text_size_x):
    center_x = (x - text_size_x) / 2
    return center_x

def get_center_y(y, text_size_y):
    center_y = (y - text_size_y) / 2
    return center_y

def draw_definition(draw, x, y, definition_data, p_data, synonyms_data):
    font_size = 28
    font = ImageFont.truetype("Quote.ttf", font_size)

    definition_1_start_y = synonyms_data[0] + synonyms_data[2]
    definition_1_end_y = p_data[0]
    definition_1_area_y = definition_1_end_y - definition_1_start_y

    definition_2_start_y = synonyms_data[1]
    definition_2_end_y = p_data[1] + p_data[2]
    definition_2_area_y = definition_2_start_y - definition_2_end_y

    for k in range(0, len(definition_data)): #Runs 2 times to display definition of 2 words
        count = len(definition_data[k])
        partition = definition_2_area_y / (count+1)
        draw_data = []
        for i in range(0, count):
            definition = definition_data[k][i][1]['definition']
            example = definition_data[k][i][1]['example']
            meaning_size = draw.textsize(definition, font)
            example_size = draw.textsize(example, font) if example != None else (0, 0)

            border = x - (x / 15)
            while (meaning_size[0] > border or example_size[0] > border): #Need to do for y as well?
                font_size -= 1
                font = ImageFont.truetype("Quote.ttf", font_size)
                meaning_size = draw.textsize(definition, font)
                example_size = draw.textsize(example, font)
            meaning_x = get_center_x(x, meaning_size[0])
            meaning_y = (definition_2_end_y + (partition * (i + 1)) - (meaning_size[1] if example != None else 0))# - meaning_size[1]/2
            example_x = get_center_x(x, example_size[0])
            example_y = (definition_2_end_y + (partition * (i + 1)))# - meaning_size[1]/2

            draw_data.append({'meaning_x' : meaning_x, 'meaning_y' : meaning_y,
                                'example_x' : example_x,'example_y' : example_y,
                                'definition' : definition, 'example' : example,
                                'font' : font, 'partOfSpeech' : definition_data[k][i][0]})
            font_size = 28
            #font = ImageFont.truetype("Quote.ttf", font_size)

        min_x = min(min([(content['meaning_x'], content['example_x']) for content in draw_data]))
        for i, content in enumerate(draw_data):
            font_ = content['font']
            example = content['example']
            meaning_y = content['meaning_y']

            draw.text((min_x, content['meaning_y']), content['definition'], font=font_)
            if example != None:
                draw.text((min_x, content['example_y']), example, font=font_)

def get_dictionary_data(words):
    data = []
    for word in words:
        url = "http://www.oxforddictionaries.com/definition/english/" + word
        page = requests.get(url, verify=False).text
        soup = BeautifulSoup(page, "lxml")

        results = soup.select('section.se1 > h3.partOfSpeechTitle >\
                                span.partOfSpeech')[:3]
        part_of_speech = [result.text for result in results]

        count = len(part_of_speech)
        definition_data = []
        for i in range(0, count):
            limit = 2 if count == 1 else 1
            results_1_raw = soup.select('div > section:nth-of-type('+str(i+1)+') \
                                        div.msDict.sense > div.senseInnerWrapper > \
                                        span.definition')[:limit]

            for j, definition in enumerate(results_1_raw):
                results_2_raw = results_1_raw[j].parent.select("span.exampleGroup.exGrBreak \
                                                                > em.example")
                example = None if not results_2_raw else results_2_raw[0].text

                dictionary = {'definition' : definition.text.strip(), 'example' : example}
                definition_data.append([part_of_speech[i], dictionary])
        data.append(definition_data)
    print data[0][0][0]
    return data

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

def get_pronunciation(words):
    return ["[kwid-nuhngk]", "[Pro-nun-ci-at-ion]"]

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

def get_words():
    url = "http://www.vocabulary.com/dictionary/randomword"
    words = []

    for x in range(0, 2):
        page = requests.get(url, verify=False).text
        soup = BeautifulSoup(page, "lxml")
        word = str(soup.select('div.wordPage')[0]['data-word']).title()
        words.append(word)

    return words

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

    synonyms_data = (synonyms_1_y, synonyms_2_y, synonyms_1_size[1]) #Return a dict instead
    return synonyms_data

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

def get_quote():
    api_url = "http://api.theysaidso.com/qod"
    default_quote = '"Don\'t cry because it\'s over, smile because it happened."'
    default_quote_author = 'Dr. Seuss'

    json = requests.get(api_url).json()
    content = json.get('contents')

    if content is not None:
        quote = content['quote']
        author = content['author']

        return (quote, author)
    else:
        return (default_quote, default_quote_author)

def lol():
    data = [
        	    [
        		    ['noun', {'definition': 'A person employed in an office or bank to keep records, accounts, and undertake other routine administrative duties:', 'example': 'a bank clerk'}],
        	        ['verb', {'definition': 'Work as a clerk:','example': 'eleven of those who left college this year are clerking in auction stores'}]
        	    ],
                [{'asdf': 'asdf'}],
        	    [
        		    ['adjective', {'definition': 'Important; famous:', 'example': 'she was a prominent member of the city council'}],
        	        ['noun', {'definition': 'A stout drab-coloured moth with tufts on the forewings which stick up while at rest, the caterpillars of which typically have fleshy growths on the back.'}]
                ]
                [{'asdf': 'asdf'}]
            ]
    print data
def main():
    #lol()
    img = Image.open("image.jpg").crop((0,0,1440,900))
    draw = ImageDraw.Draw(img)
    x, y = img.size

    words = get_words()
    print words[0], words[1]

    #quote, author = get_quote()
    #draw_quote(draw, x, y, quote, author)

    synonyms_1 = get_synonyms(words[0])
    synonyms_2 = get_synonyms(words[1])
    synonyms_data = draw_synonyms(draw, x, y, synonyms_1, synonyms_2)

    words_data = draw_words(draw, x, y, words)

    pronunciations = get_pronunciation(words)
    if pronunciations is not None:
        p_data = draw_pronunciation(draw, x, y, pronunciations, words_data)

    data = get_dictionary_data(['Clerk', 'Prominent'])
    draw_definition(draw, x, y, data, p_data, synonyms_data)


    img.save('sample-out.jpg')

if __name__ == "__main__":
    main()
