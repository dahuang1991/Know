import multiprocessing
import os
import time
import urllib.request
from multiprocessing import Pool

import requests
from lxml import html


def cbk(a, b, c):
    '''''回调函数
    @a:已经下载的数据块
    @b:数据块的大小
    @c:远程文件的大小
    '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    print(f'{os.getpid()}---------{per}%')

"""
    生产音频的id
"""

def get_url(q):
    req = requests.get(
        'http://m.ximalaya.com/explore/more_album?page=1&per_page=12000&category_id=12&condition=rank&status=0').json()[
        'html']
    reqFrom = html.fromstring(req)
    hrefs = reqFrom.cssselect('a')

    print(len(hrefs))
    for i in hrefs:
        tmpUrl = i.get('data-url').split('/')[3]
        stop = False
        page = 0
        while not stop:
            page += 1
            # print(tmpUrl)
            infoByaid = requests.get(
                f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()
            if infoByaid['next_page'] == 0:
                stop = True
                break
            sound_ids = requests.get(
                f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()[
                'sound_ids']
            for id in sound_ids:
                # print(f'get{id}')
                q.put(id)

"""
根据id下载音频
"""
def get_sound_ids(sid_q):
    while True:
        id = sid_q.get(True)
        print(os.getpid())
        if not id:
            time.sleep(0.5)
            continue
        get_info = requests.get(f'http://m.ximalaya.com/tracks/{id}.json').json()
        # print(get_info)
        if os.path.isfile(f'/data/down/mp3/test/{get_info["title"]}.m4a'):
            continue
        else:
            if not get_info["play_path_64"]:
                continue
            else:

                urllib.request.urlretrieve(f'{get_info["play_path_64"]}',f'/data/down/mp3/test/{get_info["title"]}.m4a')


def main():
    manager = multiprocessing.Manager()
    q = manager.Queue()
    p = Pool(processes=4)
    p.apply_async(get_url, args=(q,))
    for i in range(3):
        p.apply_async(get_sound_ids, args=(q,))
    p.close()
    p.join()


if __name__ == '__main__':

    main()
