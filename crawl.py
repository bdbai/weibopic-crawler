#!/usr/bin/python3

import os
import sys
import re
import requests
import json

if __name__ == '__main__' :
    if len(sys.argv) < 3:
        print('Usage: python3 crawl.py weiboname pagelimit \r\n  e.g. python3 crawl.py yangmiblog 5')
        sys.exit(0);
    
    
    if not os.path.exists('./' + sys.argv[1]) :
        os.mkdir(sys.argv[1])
    
    s = requests.Session()
    p = re.compile(".*(\\{'stage': .*?\"stage\":\"page\"\\}\\}).*")
    r = s.get('http://weibo.com/' + sys.argv[1], headers={'User-Agent' : 'Mozilla/5.0 (Mobile; Android 4.0; ARM; like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537'})
    result = p.match(r.text).group(1).replace("'", '"')
    obj = json.loads(result)['stage']['page'][2]['card_group']
    for i in obj :
        if i['card_type'] == 11 :
            itemid = i['async_api'][18:34]
            print('Found item id: ' + itemid)
            break
    for page in range(int(sys.argv[2])) :
        print('Enter page: ' + str(page)) 
        page = s.get('http://m.weibo.cn/page/json?containerid=' + itemid + '_-_WEIBO_SECOND_PROFILE_WEIBO&page=' + str(page))
        for i in json.loads(page.text)['cards'][0]['card_group'] :
            picids = i['mblog']['pic_ids']
            print('Pics found in this weibo: ' + str(len(picids)))
            for pic in picids :
                print('Downloading pic: ' + pic)
                with open(sys.argv[1] + '/' + pic + '.jpg', 'wb') as file :
                    file.write(s.get('http://ww2.sinaimg.cn/large/' + pic + '.jpg').content)
    
