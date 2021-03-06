#!/usr/bin/env python

"""
Daily clouds
"""

import datetime
import logging
import subprocess
import os
import json
import random
import pytz


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TIME_ZONE = pytz.timezone('Europe/Rome')


#RANDOM_FONTS = ["Chelsea+Market"]

def load_google_fonts():
    
    with open("google-fonts-list.json") as f:
        fonts = json.load(f)
        f = [x["family"] for x in fonts if x["category"] != 'handwriting']
    
    return f

def main():

    RANDOM_FONTS = load_google_fonts()
    
    today = datetime.datetime.now(TIME_ZONE)
    today_prefix = today.strftime("%Y%m%d-%H")
    logger.info(' ... Creating cloud for ... % s' % today_prefix )
    if not os.path.isdir(today_prefix):
        os.mkdir(today_prefix)

    today_feeds = os.path.join(today_prefix, "%s.txt" % today_prefix )
    today_frequencies = os.path.join(today_prefix, "%s.freq.txt" % today_prefix )
    today_cloud = os.path.join(today_prefix, "%s.image.png" % today_prefix )
    today_config = os.path.join(today_prefix, "%s.config.json" % today_prefix )

    if not os.path.isfile(today_feeds):
        subprocess.check_call(["python", "feedsreader.py", "feeds.txt", today_feeds])

    if not os.path.isfile(today_frequencies):
        subprocess.check_call(["python", "cloud_maker.py", today_feeds, today_frequencies, "--frequencies-only", "--min-len=2"])

    if not os.path.isfile(today_config):
        with open("prova.config.json", "rt") as f:
            base_config = json.load(f)

        base_hue = random.randint(0, 360)
        base_config["--color-func-params"] = "{\"base_hue\":%d, \"vibrance\":20}" % base_hue

        #RANDOM FONT
        base_config["--google-font"] = random.choice(RANDOM_FONTS)

        with open(today_config, "wt") as fw:
            base_config = json.dump(base_config, fw, indent=4)

    cloud_args = ["python", "cloud_maker.py", today_frequencies, today_cloud, "--from-frequencies",
        "--loadconfig", today_config]

    subprocess.check_call(cloud_args)

    logger.info(' ... Cloud done for ... % s' % today )



if __name__ == '__main__':
    main()
