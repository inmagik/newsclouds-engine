from xml.etree.ElementTree import XML
import string
import requests

"""
Read feed url and concat feed items titles
"""
def readfeedurl(feedurl, take = 10):
    # Get raw feed string from feed url
    r = requests.get(feedurl)
    # TODO: Check encoding...
    r.encoding = 'utf-8'

    # Parse raw feed string to xml
    tree = XML(r.text.strip())

    index = 0
    feedtext = ''
    printable = set(string.printable)

    # Read rss items
    for node in tree.iter('item'):

        # Limit taken items
        if not index < take:
            break

        # Get title text from the item node
        titletext = node.find('title').text.strip()

        # Remove shitty characters from jsp fucking rss feeds...
        titletext = ''.join(filter(lambda x: x in printable, titletext))

        feedtext += titletext + '\n'
        index += 1

    return feedtext

def readfeeds(feedsfile, take = 10):
    with open(feedsfile, 'r') as infile:
        feedsurls = [line.strip() for line in infile.readlines()]
        feedstext = ''
        for feedurl in feedsurls:
            # try:
                feedstext += readfeedurl(feedurl, take)
                # print feedstext
                feedstext += '\n'
            # except:
                # TODO: Better error handling...
                # pass

        # print feedstext
        return feedstext
