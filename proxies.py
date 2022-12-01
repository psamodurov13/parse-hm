import requests as rq
import functions as fn

headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
    }

proxies = [
    {'https': 'http://193.124.179.125:9765'},
    {'https': 'http://193.124.179.208:9849'},
    {'https': 'http://193.124.177.25:9548'},
    {'https': 'http://138.128.19.37:9115'},
    {'https': 'http://107.152.153.175:9255'},
    None
]


def choise_proxy():
    for i in proxies:
        response = rq.get('https://www2.hm.com/tr_tr/index.html', headers=headers, proxies=i)
        fn.logger.info(response)
        if response.status_code == 200:
            return i


def check_proxy():
    for i in proxies:
        response = rq.get('https://www2.hm.com/tr_tr/index.html', headers=headers, proxies=i)
        fn.logger.info(f'{i} - {response.status_code}')


if __name__ == '__main__':
    check_proxy()