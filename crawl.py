import sys
import re
import requests
import json

if __name__ == '__main__' :
    s = requests.Session()
    p = re.compile(".*(\\{'stage': .*?\"stage\":\"page\"\\}\\}).*")
    r = s.get('http://weibo.com/' + sys.argv[1], headers={'User-Agent' : 'Mozilla/5.0 (Mobile; Android 4.0; ARM; like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537'})
    result = p.match(r.text).group(1).replace("'", '"')
    obj = json.loads(result)['stage']['page'][2]['card_group']
    for i in obj :
        if i['card_type'] == 11 :
            itemid = i['async_api'][18:34]
            print(itemid)
            break
    for page in range(int(sys.argv[2])) : 
        page = s.get('http://m.weibo.cn/page/json?containerid=' + itemid + '_-_WEIBO_SECOND_PROFILE_WEIBO&page=' + str(page))
        for i in json.loads(page.text)['cards'][0]['card_group'] :
            picids = i['mblog']['pic_ids']
            for pic in picids :
                with open(sys.argv[1] + '/' + pic + '.jpg', 'wb') as file :
                    file.write(s.get('http://ww2.sinaimg.cn/large/' + pic + '.jpg').content)
    
