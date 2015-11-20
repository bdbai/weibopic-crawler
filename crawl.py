import re
import requests
import json

if __name__ == '__main__' :
    p = re.compile(".*(\\{'stage': .*?\"stage\":\"page\"\\}\\}).*")
    r = requests.get('http://weibo.com/photo', headers={'User-Agent' : 'Mozilla/5.0 (Mobile; Android 4.0; ARM; like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537'})
    result = p.match(r.text).group(1).replace("'", '"')
    obj = json.loads(result)['stage']['page'][2]['card_group']
    for i in obj :
        if i['card_type'] == 11 :
            card_api = 'http://m.weibo.cn' + i['async_api'] + '&callback=a'
            print(card_api)
            continue


     
