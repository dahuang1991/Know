import  urllib.request
import requests
from multiprocessing import Queue,Pool
import multiprocessing
import  crontab,time,os
from lxml import html
def cbk(a,b,c):
    '''''回调函数
    @a:已经下载的数据块
    @b:数据块的大小
    @c:远程文件的大小
    '''
    per=100.0*a*b/c
    if per>100:
        per=100
    print(f'{per}%')
def get_url(siq_q):
    req=requests.get('http://m.ximal'
                     'aya.com/explore/more_album?page=1&per_page=12000&category_id=12&condition=rank&status=0').json()['html']
    print(req)
    reqFrom=html.fromstring(req)
    hrefs=reqFrom.cssselect('a')

    print(len(hrefs))
    for i in hrefs:
        tmpUrl=i.get('data-url').split('/')[3]
        stop = False
        page = 0
        while not stop:
            page += 1
            # print(tmpUrl)
            infoByaid = requests.get(
                f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()
            if infoByaid['next_page'] == 0:
                stop = True

            sound_ids = requests.get(
                f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()[
                'sound_ids']
            for id in sound_ids:
                siq_q.put(id)


        siq_q.put(tmpUrl)
def get_sound_ids(sid_q):

    while True:
        print(os.getppid())
        tmpUrl=sid_q.get(True)
        print(tmpUrl)
        stop=False
        page=0
        while not stop:
            page+=1
            # print(tmpUrl)
            infoByaid=requests.get(f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()
            if infoByaid['next_page']==0:
                stop=True

            sound_ids=requests.get(f'http://m.ximalaya.com/album/more_tracks?url=%2Falbum%2Fmore_tracks&aid={tmpUrl}&page={page}').json()['sound_ids']
            for id in sound_ids:
                # print(id)
                getInfo=requests.get(f'http://m.ximalaya.com/tracks/{id}.json').json()
                if os.path.isfile(f'/data/down/mp3/{getInfo["title"]}.m4a'):
                    continue
                print(f'/data/down/mp3/{getInfo["title"]}.m4a{os.getppid()}')
                # urllib.request.urlretrieve(f'{getInfo["play_path_64"]}',f'/data/down/mp3/{getInfo["title"]}.m4a',)


            # print(sound_ids)
        #     for k in range(len(sound_urls)):
    #         sound_url=sound_urls[k].get('sound_url')
    #         print(sound_url)
    #         if(sound_url[0:4]=='http'):
    #             urllib.request.urlretrieve(sound_url,f'/data/down/mp3/{titles[k]}.m4a',cbk)
    #         else:
    #             print('http://audio.pay.xmcdn.com/download/1.0.0/'+sound_url)
    #             try :
    #                 urllib.request.urlretrieve('http://audio.pay.xmcdn.com/download/1.0.0/'+sound_url, f'/data/down/mp3/{titles[k]}.m4a', cbk)
    #             except urllib.error.HTTPError:
    #                 break
    #


def main():

    manager = multiprocessing.Manager()

    q = manager.Queue()
    p = Pool(processes=1)
    pw1 = p.apply_async(get_url, args=(q,))
    p1 = Pool(processes=4)
    time.sleep(0.1)
    for i in range(4):
        time.sleep(i)
        pr1 = p1.apply_async(get_sound_ids, args=(q,))
    p1.close()
    p1.join()

    p.close()
    p.join()
    print(1)

if __name__ == '__main__':
    main()



