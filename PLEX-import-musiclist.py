#coding=utf-8
## python 3
# pip install plexapi
#使用帮助请访问 http://www.plexmedia.cn

import urllib
import requests
import http.client
import json
import sys
import urllib.request
import difflib
import re
import string
from urllib.parse import quote
from urllib.parse import urlencode
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from plexapi.myplex import MyPlexDevice
from plexapi.myplex import ResourceConnection
WangYiYun_Songs_Url = 'http://music.163.com/api/song/detail/?id=&ids=[%s]'
WangYiYun_Playlist_Url =  'https://music.163.com/api/v1/playlist/detail?id=%s'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'origin': 'https://y.qq.com',
    'referer': 'https://y.qq.com/portal/playlist.html'
}
 
 
def fetch_url(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code in [200, 201]:
            return r.json()
    except Exception as e:
        print(e)
def get_record(url):
    resp = urllib.request.urlopen(url)
    ele_json = json.loads(resp.read())
    return ele_json


PLEX_TOKEN = ""
url = 'https://music.163.com/api/v1/playlist/detail?id=634489'
def fetchPlexApi(path='', method='GET', getFormPlextv=False, token=PLEX_TOKEN, params=None):
        """a helper function that fetches data from and put data to the plex server"""
        headers = {'X-Plex-Token': token,
                'Accept': 'application/json'}
        if getFormPlextv:
            url = 'plex.tv'        
            connection = http.client.HTTPSConnection(url)
        else:
            url = PLEX_URL.rstrip('/').replace('http://','')
            connection = http.client.HTTPConnection(url)
        try:
            if method.upper() == 'GET':
                pass
            elif method.upper() == 'POST':
                headers.update({'Content-type': 'application/x-www-form-urlencoded'})
                pass
            elif method.upper() == 'PUT':
                pass
            elif method.upper() == 'DELETE':
                pass
            else:
                print("Invalid request method provided: {method}".format(method=method))
                connection.close()
                return

            connection.request(method.upper(), path , params, headers)     
            response = connection.getresponse()         
            r = response.read()             
            contentType = response.getheader('Content-Type')      
            status = response.status    
            connection.close()

            if response and len(r):     
                if 'application/json' in contentType:         
                    return json.loads(r)
                elif 'application/xml' in contentType:
                    return xmltodict.parse(r)
                else:
                    return r
            else:
                return r

        except Exception as e:
            connection.close()
            print("Error fetching from Plex API: {err}".format(err=e))

def uniqify(seq):
    # Not order preserving
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()

#qq音乐歌单获取
def get_song_info(disstid):
    url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?'
    params = {
        'type': '1',
        'json': '1',
        'utf8': '1',
        'onlysong': '0',
        'disstid': disstid,
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
    }
    url += urlencode(params)
    result = fetch_url(url)
    dissname = result['cdlist'][0]['dissname']
    dissdesc = result['cdlist'][0]['desc']
    songlist = result['cdlist'][0]['songlist']
    #print(dissdesc)
    for song in songlist:
        strMediaMid = song['strMediaMid']
        songMid = song['songmid']
        songname = song['songname']
        singer = song['singer'][0]['name']
        yield strMediaMid, songMid, songname, singer, dissname, dissdesc

def getqqmusiclist(dissid):
    #for item in get_dist_info(page):
    #    print(item)
    #    dissid, dissname = item
    #dissid = '7693483117'
    song_list = []
    playlist_info = {}

    for item in get_song_info(dissid):
        song_list1= {}
        strMediaMid, songMid, songname,singer, dissname, dissdesc= item
        singer = singer
        #vkey = get_vkey(songMid)
        pattern = re.compile(r'[\\/:：*?"<>|\r\n]+')
        songname = re.sub(pattern, " ", songname)
        dissname = re.sub(pattern, " ", dissname)
        #print(songname + '--' + singer)
        song_list1.update(name = songname,singername = singer)
        #print(song_list1)
        song_list.append(song_list1)
    playlist_info.update(name = dissname,summary =dissdesc,songlist = song_list )
    #print(playlist_info)
    return(playlist_info) 
    
                
if __name__ == '__main__':

    #got token.url
    print("欢迎使用PLEX导入网易云、QQ音乐歌单， 使用帮助请访问 http://www.plexmedia.cn")
    PLEX_URL = input('请输入你的plex服务器地址（示例：http://192.168.31.120:32400）：')
    PLEX_TOKEN = input('请输入你的token：')
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    machineId = plex.machineIdentifier
    playlist_source = input('请输入歌单来源（输入数字）：1.网易云音乐 2.QQ音乐 ：')
    #输入歌单的id
    #PLAYLIST_ID = '2829816518'      #网易云歌单
    #PLAYLIST_ID = '2370564757'     #QQ歌单
    PLAYLIST_ID = input ('请输入网易云/QQ音乐歌单ID: ')
    #print(getqqmusiclist('7693483117')) 
    #选择新建歌单或添加至现有歌单
    if_new_playlist = input('是否将云歌单内的歌曲加入现有播放列表（输入数字）：1.加入现有列表 2.根据歌单重新创建 ：')
    if if_new_playlist == '1' :
        for playlist in plex.playlists():
            print(playlist)
        local_playlist_id = input('请输入要加入的歌曲列表id:(以上列表中的数字): ')
    #获取歌单内的歌曲   
    track_id = []
    tracks_unfound = []
    tracks_added = []
    isfirstmatch = False
    if if_new_playlist == '2':
        isfirstmatch = True

#网易云音乐
    if playlist_source == '1' :
        playlist = get_record(WangYiYun_Playlist_Url % PLAYLIST_ID)
        for trackid in playlist['playlist']['trackIds']:
            track_id.append(str(trackid['id']))
        playlist_title = playlist['playlist']['name'].replace(" ", "")
        try:
            playlist_summary = playlist['playlist']['description'].replace("\n", ",").replace(" ", ",")
        except:
            pass
        print('歌单名称： '+ playlist_title)
        #拆分歌单
        print('开始导入歌单')
        for i in range(0,len(track_id),50):
            track_ids = ",".join(track_id[i:i+50])
            songs = get_record(WangYiYun_Songs_Url % track_ids)
            #在媒体库中搜索歌曲
            for song in songs['songs'] :

                song_name = re.sub(u"\\(.*?\\)|\\（.*?）|\\[.*?]", "", song['name']) #去除歌名中括号的内容 例如（live）
                print(song_name)
                #print(re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", a))
                
                if plex.search(song_name):
                    ismatch = False
                    for localsong in plex.search(song_name):
                        #ismatch = False             #判断搜索到结果，但是结果可能不是track或者track不匹配
                        if localsong.type == 'track' :
                            song_score = 0
                            artist_score = 0
                            song_score = difflib.SequenceMatcher(None, song_name, localsong.title).quick_ratio() * 95
                            artist_score = difflib.SequenceMatcher(None, song['artists'][0]['name'], localsong.grandparentTitle).quick_ratio() * 10
                            if song_score + artist_score > 100 :
                                ismatch = True
                                #如果选择新创建歌单 则第一首歌执行创建歌单操作
                                if isfirstmatch :
                                    url1 = '/playlists?uri=server%3A%2F%2F' + machineId + '%2Fcom.plexapp.plugins.library%2Flibrary%2Fmetadata%2F' + str(localsong.ratingKey) + '&includeExternalMedia=1&title=' + playlist_title + '&smart=0&type=audio&'
                                    url2 = quote(url1,safe=string.printable)
                                    #print(url2)
                                    data = fetchPlexApi(url2,"POST",token=PLEX_TOKEN)
                                    tracks_added.append(song_name + ' -- ' + song['artists'][0]['name'])
                                    local_playlist_id = data['MediaContainer']['Metadata'][0]['ratingKey']
                                    #print(local_playlist_id)
                                    try:
                                        data1 = fetchPlexApi(quote('/playlists/'+ local_playlist_id +'?includeExternalMedia=1&summary=' + playlist_summary + '&',safe=string.printable),"PUT",token=PLEX_TOKEN)
                                    except:
                                        pass
                                    isfirstmatch = False
                                    break
                                tracks_added.append(song_name + ' -- ' + song['artists'][0]['name'])
                                #print(localsong.title)                    
                                #print(song['artists'][0]['name'])
                                #print(localsong.ratingKey)
                                #print('/playlists/'+ '32680' + Uri + str(localsong.ratingKey) + '&includeExternalMedia=1&X-Plex-Token=' + PLEX_TOKEN)
                                data = fetchPlexApi('/playlists/'+ local_playlist_id + '/items?uri=server%3A%2F%2F' + machineId + '%2Fcom.plexapp.plugins.library%2Flibrary%2Fmetadata%2F' + str(localsong.ratingKey) + '&includeExternalMedia=1&',"PUT",token=PLEX_TOKEN)
                                break
                    if not ismatch :
                        #print('搜索到结果但是不匹配')
                        tracks_unfound.append(song['name'] + ' -- ' + song['artists'][0]['name'])                                        
                else:
                    tracks_unfound.append(song['name'] + ' -- ' + song['artists'][0]['name'])

    #QQ音乐歌单获取                
    if playlist_source == '2' :
        songs = getqqmusiclist(PLAYLIST_ID)
        playlist_title = songs['name'].replace(" ", "")
        try:
            playlist_summary = songs['summary'].replace("\n", ",").replace(" ", ",")
        except:
            pass       
        print(playlist_title)
        print(playlist_summary)
        for song in songs['songlist'] :
                song_name = re.sub(u"\\(.*?\\)|\\（.*?）|\\[.*?]", "", song['name']) #去除歌名中括号的内容 例如（live）
                print(song_name)
                #print(re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", a))
                
                if plex.search(song_name):
                    ismatch = False
                    for localsong in plex.search(song_name):
                        #ismatch = False             #判断搜索到结果，但是结果可能不是track或者track不匹配
                        if localsong.type == 'track' :
                            song_score = 0
                            artist_score = 0
                            song_score = difflib.SequenceMatcher(None, song_name, localsong.title).quick_ratio() * 95
                            artist_score = difflib.SequenceMatcher(None, song['singername'], localsong.grandparentTitle).quick_ratio() * 10
                            if song_score + artist_score > 100 :
                                ismatch = True
                                #如果选择新创建歌单 则第一首歌执行创建歌单操作
                                if isfirstmatch :
                                    url1 = '/playlists?uri=server%3A%2F%2F' + machineId + '%2Fcom.plexapp.plugins.library%2Flibrary%2Fmetadata%2F' + str(localsong.ratingKey) + '&includeExternalMedia=1&title=' + playlist_title + '&smart=0&type=audio&'
                                    url2 = quote(url1,safe=string.printable)
                                    #print(url2)
                                    data = fetchPlexApi(url2,"POST",token=PLEX_TOKEN)
                                    tracks_added.append(song_name + ' -- ' + song['singername'])
                                    local_playlist_id = data['MediaContainer']['Metadata'][0]['ratingKey']
                                    try:
                                        data1 = fetchPlexApi(quote('/playlists/'+ local_playlist_id +'?includeExternalMedia=1&summary=' + playlist_summary + '&',safe=string.printable),"PUT",token=PLEX_TOKEN)
                                    except:
                                        pass
                                    isfirstmatch = False
                                    break
                                tracks_added.append(song_name + ' -- ' + song['singername'])
                                #print(localsong.title)                    
                                #print(song['artists'][0]['name'])
                                #print(localsong.ratingKey)
                                #print('/playlists/'+ '32680' + Uri + str(localsong.ratingKey) + '&includeExternalMedia=1&X-Plex-Token=' + PLEX_TOKEN)
                                data = fetchPlexApi('/playlists/'+ local_playlist_id + '/items?uri=server%3A%2F%2F' + machineId + '%2Fcom.plexapp.plugins.library%2Flibrary%2Fmetadata%2F' + str(localsong.ratingKey) + '&includeExternalMedia=1&',"PUT",token=PLEX_TOKEN)
                                break
                    if not ismatch :
                        #print('搜索到结果但是不匹配')
                        tracks_unfound.append(song['name'] + ' -- ' + song['singername'])                                        
                else:
                    tracks_unfound.append(song['name'] + ' -- ' + song['singername'])
    print('以下歌曲没有在媒体库中找到')
    print(tracks_unfound)
    print(len(tracks_unfound))
    print('以下歌曲已经添加到歌单')
    print(tracks_added)
    print(len(tracks_added))
            
