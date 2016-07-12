#!/usr/bin/python3

import os
import re
import requests
import json
from argparse import ArgumentParser
from contextlib import closing

COMMON_REQUEST_HEADER = { 'User-Agent' : 'Mozilla/5.0 (Mobile; Android 4.0; ARM; like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537' }
ITEM_JSON_REGEX = re.compile(".*(\\{'stage': .*?\"stage\":\"page\"\\}\\}).*")
USER_URL_PATTERN = 'http://weibo.com/{0}'
PAGE_URL_PATTERN = 'http://m.weibo.cn/page/json?containerid={0}_-_WEIBO_SECOND_PROFILE_WEIBO&page={1}'
PIC_URL_PATTERN = 'http://ww2.sinaimg.cn/large/{0}.jpg'

class WeibopicCrawler(object):
    """Crawler for the specific Weibo user."""

    def __init__(self, weibo_name, force = False):
        """Initialize a new crawler object.

        ``weibo_name`` is either a user's Weibo name or his ID. Will be
        appended to the end of 'weibo.com/' directly.
        ``force`` will clean any pics downloaded from the user immediately if
        is set to ``True``.
        """
        self.item_id = None
        self.weibo_name = weibo_name
        if force:
            self.clear_cache()
        self.ensure_dir()
        self.request_session = requests.Session()

    def log(self, line, line_end = '\n'):
        """Output a line of log."""
        print(line, end=line_end)

    def clear_cache(self):
        """Delete the user's directory recursively."""
        for root, dirs, files in os.walk(self.weibo_name):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.weibo_name)

    def ensure_dir(self):
        """Ensure the user's directory exists'"""
        if not os.path.exists(self.weibo_name):
            os.mkdir(self.weibo_name)

        self.temp_file = self.weibo_name + '/tempfile'
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def get_user_item_id(self):
        """Get the user's ``async_api`` ID for future use."""
        if self.item_id is not None:
            return self.item_id

        response = self.request_session.get(USER_URL_PATTERN.format(self.weibo_name), headers=COMMON_REQUEST_HEADER)
        internal_json = ITEM_JSON_REGEX.match(response.text).group(1).replace("'", '"')
        cards = json.loads(internal_json)['stage']['page'][2]['card_group']

        api_card = [card for card in cards if card['card_type'] == 11][0]
        self.item_id = api_card['async_api'][18:34]
        self.log('Found item id: ' + self.item_id)
        return self.item_id

    def get_pics_from_page(self, page_id):
        """Yields all pic IDs from the specific page."""
        response = self.request_session.get(PAGE_URL_PATTERN.format(self.item_id, page_id))
        for weibo in json.loads(response.text)['cards'][0]['card_group']:
            pic_ids = weibo['mblog']['pic_ids']
            for pic_id in pic_ids:
                yield pic_id

    def download_pic(self, pic_id):
        """Save the pic to disk."""
        file_name = '{0}/{1}.jpg'.format(self.weibo_name, pic_id)
        if os.path.exists(file_name):
            self.log('Skipped: ' + pic_id)
        else:
            self.log('Downloading pic: ' + pic_id, '')
            with open(self.temp_file, 'wb') as file:
                with closing(self.request_session.get(PIC_URL_PATTERN.format(pic_id), stream=True)) as response_stream:
                    for chunk in response_stream.iter_content(5120):
                        file.write(chunk)
            os.rename(self.temp_file, file_name)
            self.log(' Done!')

    def crawl_page(self, page_id):
        """Crawl from a page.

        ``page_id`` is the page to be crawled from, starting from 1.
        """
        self.get_user_item_id()
        self.log('Entering page ' + str(page_id))
        for pic_id in self.get_pics_from_page(page_id):
            self.download_pic(pic_id)

def get_options():
    """Parse command line arguments."""
    parser = ArgumentParser()
    parser.add_argument('-f', '--force', dest='force', action='store_true', help='Clear cache before downloading')
    parser.add_argument('weibo_name', metavar='ID', type=str, help='Weibo name or number')
    parser.add_argument('maxpage', metavar='N', type=int, help='Maximum pages to crawl')
    return parser.parse_args()

def main():
    options = get_options()
    crawler = WeibopicCrawler(options.weibo_name, options.force)
    for page_id in range(options.maxpage):
        try:
            crawler.crawl_page(page_id + 1)
        except KeyboardInterrupt as ex:
            print('User interrupted.')
            exit(0)
    print('Crawling finished!')

if __name__ == '__main__':
    main()
