from copy import copy
import sys
import codecs
import nltk
from nltk.corpus import stopwords
import numpy as np
import os
import re
from wordcloud import WordCloud, ImageColorGenerator
import random
from PIL import Image
from icon_font_to_png import IconFont, FontAwesomeDownloader
from icon_font_to_png.icon_font_downloader import IconFontDownloader
from fontdump.core import GoogleFontGroup
import requests
import functools


class IoniconsDownloader(IconFontDownloader):
    """
    Ionic icon font downloader
    Project page:
        http://ionicons.com/
    """
    css_url = ('https://raw.githubusercontent.com/driftyco/ionicons/master/css/ionicons.css')
    ttf_url = ('https://raw.githubusercontent.com/driftyco/ionicons/master/fonts/ionicons.ttf')

    def get_latest_version_number(self):
        return self._get_latest_tag_from_github(
            'https://api.github.com/repos/github/ionicons'
        )


CUR_DIR = os.path.dirname(__file__)
FA_PATH = os.path.join(CUR_DIR, "exported/")
FONTS_PATH = os.path.join(CUR_DIR, "fonts/")
font_path = "/Library/Fonts/Michroma.ttf"


WORD_CLOUD_DEFAULTS = {
    "background_color" : "white",
    "max_words" : 400,
    "width": 1000,
    "height": 500,
    "max_font_size": 250,
    "mask": None,
    "font_path": None,
    "relative_scaling": None
}




def compute_frequencies(
    text,
    encoding="latin-1", language='italian', min_len=3):

    # NLTK's default stopwords. musst be loaded if not present
    default_stopwords = set(nltk.corpus.stopwords.words(language))
    words = nltk.word_tokenize(text)
    # default_stopwords = set(nltk.corpus.stopwords.words(language))
    # fp = codecs.open(input_file, 'r', encoding)
    # words = nltk.word_tokenize(fp.read())

        # Remove punctuation
        # text = text.translate(None, string.punctuation)
    # Remove single-character tokens (mostly punctuation)
    words = [word for word in words if len(word) >= int(min_len)]

    # Remove numbers
    #words = [word for word in words if not word.isnumeric()]

    # Lowercase all words (default_stopwords are lowercase too)
    #words = [word.lower() for word in words]

    # Stemming words seems to make matters worse, disabled
    #stemmer = nltk.stem.snowball.SnowballStemmer('italian')
    #words = [stemmer.stem(word) for word in words]

    # Remove stopwords
    words = [word for word in words if word.lower() not in default_stopwords]

    common_articleswords = ['foto', 'video', 'foto|video', 'video|foto', 'anni', 'giorni', 'sono']
    words = [word for word in words if word.lower() not in common_articleswords]

    # Calculate frequency distribution
    fdist = nltk.FreqDist(words)

    # Output top 50 words
    frequencies = []
    for word, frequency in fdist.most_common(400):
        print('%s;%d' % (word, frequency))
        frequencies.append((word, frequency))
        # frequencies.append((word.encode(encoding), frequency))

    return frequencies


def load_frequencies(filename):
    with open(filename, "rt") as f:
        txtdata = f.read()

    lines = txtdata.split("\n")
    pieces = [line.split(",") for line in lines]
    data = [[piece[0], int(piece[1])] for piece in pieces if piece and len(piece)==2]
    return data


def save_frequencies(data, filename):
    txtdata = "\n".join([", ".join(str(x) for x in f) for f in data])
    with open(filename, "wt") as f:
        f.write(txtdata)


def make_mask(icon, size=1000, source="fa", color="black", background_color='white'):

    if source == 'image':
        downloader = None

    if source =='ionic':
        downloader = IoniconsDownloader(FA_PATH)

    elif source == 'fa':
        downloader = FontAwesomeDownloader(FA_PATH)

    if downloader:
        downloader.download_files()

        icon_font = IconFont(downloader.css_path, downloader.ttf_path, keep_prefix=True)
        icon_font.export_icon(icon, size, color='black', scale='auto',
            filename=None, export_dir='exported')
        #icon = "circle"
        # http://stackoverflow.com/questions/7911451/pil-convert-png-or-gif-with-transparency-to-jpg-without
        icon_path = FA_PATH + "%s.png" % icon
    else:
        icon_path = icon
    #icon_path = os.path.join(d, "lord-ganesh.jpg")
    icon = Image.open(icon_path)
    if source == 'image':
        icon = icon.resize((size, size), Image.ANTIALIAS)

    mask = Image.new("RGB", icon.size, background_color)
    mask.paste(icon,icon)
    mask = np.array(mask)

    return mask


def get_google_font(google_fonts_url):
    if not os.path.isdir(FONTS_PATH):
        os.mkdir(FONTS_PATH)

    g = GoogleFontGroup(google_fonts_url)
    for font in g.fonts:
        if 'ttf' not in font.styles:
            return None
        font_style = font.styles['ttf']
        pattern = r'url\((.+)\) '
        font_url = re.findall(pattern, font_style.src)[0]
        r = requests.get(font_url, stream=True)
        if r.status_code == 200:
            font_dest = os.path.join(FONTS_PATH, font.primary_name+".ttf")
            with open(font_dest, "wb") as fontfile:
                for chunk in r:
                    fontfile.write(chunk)
            return font_dest

    return None



def save_cloud(frequencies, output, options={}, color_func=None,canvas_width=0, canvas_height=0):
    base_options = copy(WORD_CLOUD_DEFAULTS)
    base_options.update(options)
    clean_options = { x : base_options[x] for x in base_options if base_options[x] is not None}

    wordcloud = WordCloud(**clean_options).generate_from_frequencies(frequencies)

    if(color_func):
        wordcloud = wordcloud.recolor(color_func=color_func)

    image = wordcloud.to_image()

    if clean_options.get("height") != clean_options.get("width") and not canvas_width and not canvas_height:
        canvas_height = clean_options.get("height")
        canvas_width = clean_options.get("width")

    if(canvas_width and canvas_height):
        final_image =  Image.new(image.mode, (canvas_width, canvas_height), clean_options.get("background_color"))
        offset = (int((final_image.size[0] - image.size[0]) / 2), int((final_image.size[1] - image.size[1]) / 2))

        final_image.paste(image, offset)
        return final_image.save(output)

    return image.save(output)


def get_color_func(base_hue, saturation=85, vibrance=0, max_l=90, min_l=40):

    def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        if(kwargs.get('vibrance', None)):
            vibrance = kwargs.get('vibrance')
            base_hue = kwargs.get('base_hue')
            min_l = kwargs.get('min_l')
            max_l = kwargs.get('max_l')
            base_hue = random.randint(base_hue-vibrance, base_hue+vibrance) % 360
        return "hsl(%s, %s%%, %s%%)" % (base_hue, saturation, random.randint(min_l, max_l))

    return functools.partial(grey_color_func, base_hue=base_hue, vibrance=vibrance,
        min_l=min_l, max_l=max_l)
