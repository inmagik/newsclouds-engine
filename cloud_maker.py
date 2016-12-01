"""Cloudmaker.

Usage:
  cloud_maker.py (-h | --help)
  cloud_maker.py --version
  cloud_maker.py <textfile> <output> [ --size=<sizestring> ]
    [ --background-color=<bk> ] [ --google-font=<google-font> ]
    [ --fa-mask=<fa-mask> | --ionic-mask=<ionic-mask> | --image-mask=<image-mask> ]
    [ --relative-scaling=<relative-scaling> ]
    [ --max-font-size=<max-font-size> ]
    [ --canvas=<canvasstring> ]
    [ --color-func=<color-func-name>  --color-func-params=<color-func-params> ]
    [--logconfig] [--loadconfig=<savedconfig>]
    [--encoding=<encoding>] [--language=<language>] [--min-len=<min-len>]
    [--max-words=<max-words>]
    [--frequencies-only] [--from-frequencies]

Options:
  -h --help     Show this screen.
  --version     Show vesion.
  --logconfig   Writes a log (<output>.cloudconfig.json)
  --loadconfig=<savedconfig>    Loads a config. Can be overridden with other arguments.
  --fa-mask=<fa-mask>     Use fontawesome mask.
  --ionic-mask=<ionic-mask> Use ionicons mask.
  --google-font=<google-font>   Uses the specified font form Goggle fonts (name).
  --background-color=<bk>  Set background color.
  --size=<sizestring>     Set size, defaults to 1000x1000.
  --relative-scaling=<relative-scaling>     Sets relative scaling.
  --max-font-size=<max-font-size>   Sets max font size.
  --canvas=<canvasstring>   Sets size for the canvas. Image will be placed in center.
  --color-func=<color-func-name> Sets color func name.
  --color-func-params=<color-func-params> JSON params for color func.
  --encoding=<encoding>  Text encoding]
  --language=<language> Text language
  --min-len=<min-len>   Min len of words to draw [default: 3]
  --max-words=<max-words> Words in the cloud



"""
#TODO: COLORING FUNCTION (other types/params)
#TODO: CONSIDER OTHER word_cloud opts (ex.)

import sys
import json
from copy import copy
from docopt import docopt
from clouds import ( compute_frequencies, load_frequencies, save_frequencies,
    save_cloud, make_mask, get_google_font, get_color_func)
import os
import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    arguments = docopt(__doc__, version='Cloudmaker 1.0')

    if arguments['--loadconfig']:

        with open(arguments['--loadconfig']) as f:
            base_config = json.load(f)

        for x in base_config:
            if (x not in arguments or arguments[x] is None) and base_config[x] is not None:
                arguments[x] = base_config[x]

    arguments['--size'] = arguments['--size'] or "1000x1000"
    arguments['--encoding'] = arguments['--encoding'] or "latin-1"
    arguments['--language'] = arguments['--language'] or "italian"
    arguments['--background-color'] = arguments['--background-color'] or "white"

    size_pieces = arguments['--size'].lower().split("x")

    if len(size_pieces) == 1:
        width = int(size_pieces[0])
        height = width
    if len(size_pieces) == 2:
        width = int(size_pieces[0])
        height = int(size_pieces[1])

    min_dimension = min([width, height])

    options = {
        "mask" : None,
        "font_path" : None,
        "background_color" : arguments['--background-color'],
        "max_font_size" : None,
        "width" : width,
        "height" : height,
        "color_func" : None
    }

    print(options)

    if not arguments['--from-frequencies']:

        with open(arguments['<textfile>'], "r") as textfile:
            text = textfile.read()

        logger.info(' ... Computing frequencies from %s ...' % arguments['<textfile>'])
        frequencies = compute_frequencies(
            text,
            arguments['--encoding'],
            language=arguments['--language'],
            min_len=arguments['--min-len'])

    else:
        logger.info(' ... Loading frequencies from %s ...' % arguments['<textfile>'])
        frequencies = load_frequencies(arguments['<textfile>'])

    if arguments['--frequencies-only']:
        logger.info(' ... Writing frequencies file %s ...' % arguments['<output>'])
        save_frequencies(frequencies, arguments['<output>'])
        sys.exit(0)


    if not os.path.isdir("exported"):
        os.mkdir("exported")

    if arguments['--google-font']:
        font_name = arguments['--google-font']
        logger.info(' ... Using font ... % s' % font_name)
        font_url = "https://fonts.googleapis.com/css?family=%s" % font_name
        options["font_path"] = get_google_font(font_url)


    if arguments['--fa-mask']:
        logger.info(' ... Using mask ... % s' % arguments['--fa-mask'])
        options["mask"] = make_mask(
            arguments['--fa-mask'],
            size=min_dimension
        )

    if arguments['--ionic-mask']:
        logger.info(' ... Using mask ... % s' % arguments['--ionic-mask'])
        options["mask"] = make_mask(
            arguments['--ionic-mask'],
            source = 'ionic',
            size=min_dimension
        )

    if arguments['--image-mask']:
        logger.info(' ... Using image mask ... % s' % arguments['--image-mask'])
        options["mask"] =  make_mask(
            arguments['--image-mask'],
            source = 'image',
            size=min_dimension
        )

    if arguments['--max-font-size']:
        logger.info(' ... Using max font size ... % s' % arguments['--max-font-size'])
        try:
            options["max_font_size"] = int(arguments['--max-font-size'])
        except:
            logger.error("!! Invalid value for max-font-size, skipping")


    if arguments['--relative-scaling']:
        try:
            options['relative_scaling'] = float(arguments['--relative-scaling'])
        except:
            logger.error('!! Wrong value for relative-scaling, skipping')


    if arguments['--color-func'] and arguments['--color-func-params']:
        color_func_params = json.loads(arguments['--color-func-params'])
        if arguments['--color-func'].lower() == 'hue-based':
            options['color_func'] = get_color_func(**color_func_params)


    logger.info(' ... Saving to file (%s) ...' % arguments['<output>'])

    arguments['--canvas'] = arguments['--canvas'] or "0x0"
    canvas_pieces = arguments['--canvas'].lower().split("x")

    if len(canvas_pieces) == 1:
        canvas_width = int(canvas_pieces[0])
        canvas_height = canvas_width
    if len(canvas_pieces) == 2:
        canvas_width = int(canvas_pieces[0])
        canvas_height = int(canvas_pieces[1])

    if arguments['--max-words']:
        options['max_words'] = int(arguments['--max-words'])

    save_cloud(
        frequencies,
        arguments['<output>'],
        options=options,
        color_func=None,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
    )
    """
    if arguments['--run']:
        logger.info(' ... Running ...')
        dailydir = 'dailyclouds/' + datetime.date.today().strftime("%Y%m%d")
        os.mkdir(dailydir)
        save_cloud(
            frequencies,
            dailydir + '/newsimage.jpg',
            options=options,
            color_func=None,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        )
        with open(dailydir + '/newstext.txt', "w") as f:
            f.write(text)
    """


    if arguments['--logconfig']:
        logger.info(' ... Writing config ...')
        with open(arguments['<output>'] + ".cloudconfig.json", "wb") as f:
            json.dump(arguments, f, indent=2)


if __name__ == '__main__':
    main()
