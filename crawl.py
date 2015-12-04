#!/usr/bin/python3

import os
import sys
import re
import requests
import json

if __name__ == '__main__' :
    if len(sys.argv) < 3:
        print('Usage: python3 [-f] crawl.py weiboname pagelimit \r\n -f\t Force download. \r\n  e.g. python3 crawl.py yangmiblog 5')
        sys.exit(0);
    
    if sys.argv[1] == '-f' :
        weibo_name = sys.argv[2]
        try :
            for root, dirs, files in os.walk('./' + weibo_name) :
                for name in files :
                    os.remove(os.path.join(root, name))
                for name in dirs :
                    os.rmdir(os.path.join(root, name))
            os.rmdir('./' + weibo_name)
        except Exception as e :
            print('Error occurred while deleting the directory.')
            print(e)
    else :
        weibo_name = sys.argv[1]
    page_limit = sys.argv[-1]
    
    if not os.path.exists('./' + weibo_name) :
        os.mkdir(weibo_name)
    
    temp_file = './' + weibo_name + '/tempfile'
    if os.path.exists(temp_file) :
        os.remove(temp_file)

    s = requests.Session()
    p = re.compile(".*(\\{'stage': .*?\"stage\":\"page\"\\}\\}).*")
    r = s.get('http://weibo.com/' + weibo_name, headers={'User-Agent' : 'Mozilla/5.0 (Mobile; Android 4.0; ARM; like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537'})
    result = p.match(r.text).group(1).replace("'", '"')
    obj = json.loads(result)['stage']['page'][2]['card_group']
    for i in obj :
        if i['card_type'] == 11 :
            itemid = i['async_api'][18:34]
            print('Found item id: ' + itemid)
            break
    for page_index in range(int(page_limit)) :
        page = page_index + 1
        print('Enter page: ' + str(page))
        page = s.get('http://m.weibo.cn/page/json?containerid=' + itemid + '_-_WEIBO_SECOND_PROFILE_WEIBO&page=' + str(page))
        for i in json.loads(page.text)['cards'][0]['card_group'] :
            picids = i['mblog']['pic_ids']
            print('Pics found in this weibo: ' + str(len(picids)))
            for pic in picids :
                file_name = weibo_name + '/' + pic + '.jpg'
                if os.path.exists(file_name) :
                    print('Skipped: ' + pic)
                else :
                    print('Downloading pic: ' + pic)
                    try :
                        with open(temp_file, 'wb') as file :
                            file.write(s.get('http://ww2.sinaimg.cn/large/' + pic + '.jpg').content)
                        os.rename(temp_file, file_name)
                    except KeyboardInterrupt as e :
                        print('User interrupted.')
                        sys.exit(0)
                    except Exception as e :
                        print('Error occurred.')
                        print(e)

