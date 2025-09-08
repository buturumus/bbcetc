#!/usr/bin/python3

import os
import re
import requests
import youtube_dl
import ffmpeg

BASE_DIR = '/base/'
TMP_DIR = BASE_DIR + 'tmp/'
WWW_DIR = BASE_DIR + 'www/'
TMP_EXT = '.tmp'
OUT_EXT = '.mp3'
UA = "Mozilla/5.0 (X11; Linux i686; rv:52.0) Gecko/20100101 Firefox/52.0"


class PodcastRemake():
    name = ''
    origin_url = ''
    vol_level = ''

    def __init__(self, kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def dl(self, url):
        try:
            # dl.target media file
            if os.path.exists(TMP_DIR + self.name + TMP_EXT):
                os.remove(TMP_DIR + self.name + TMP_EXT)
            r = requests.get(url)
            f = open(TMP_DIR + self.name + TMP_EXT, 'wb')
            f.write(r.content)
            f.close()
            # recode it
            (
                ffmpeg
                .input(TMP_DIR + self.name + TMP_EXT)
                .audio.filter('volume', self.vol_level)
                .output(
                    WWW_DIR + self.name + OUT_EXT,
                    format='mp3',
                    acodec='mp3',
                    audio_bitrate=64000,
                )
                .run(overwrite_output=True)
            )
            os.remove(TMP_DIR + self.name + TMP_EXT)
        except:
            return


class BbcPodcastRemake(PodcastRemake):

    def __init__(self, *args):
        super().__init__(*args)

    def dl(self, url = ''):
        try:
            # 1st dl: index html to determine target url
            url_key = (
                requests.get(self.origin_url)
                .text
                .partition('www.bbc.co.uk/sounds/play/')[2]
                .partition('"')[0]
            )
            next_url = 'https://www.bbc.co.uk/sounds/play/' + url_key
            # 2nd (not complete) dl: find format out
            you_dl_opts = {
                'user_agent': UA,
                'no_check_certificate': True,
            }
            meta = (
                youtube_dl.YoutubeDL(you_dl_opts)
                .extract_info(next_url, download=False)
            )
            format = meta.get('formats', [meta])[-1]['format_id']
            # 3rd dl.: target media
            if os.path.exists(TMP_DIR + self.name + TMP_EXT):
                os.remove(TMP_DIR + self.name + TMP_EXT)
            you_dl_opts.update({
                'format': format,
                'outtmpl': TMP_DIR + self.name + TMP_EXT,
            })
            youtube_dl.YoutubeDL(you_dl_opts).download([next_url])
            # recode it
            (
                ffmpeg
                .input(TMP_DIR + self.name + TMP_EXT)
                .audio.filter('volume', self.vol_level)
                .output(
                    WWW_DIR + self.name + OUT_EXT,
                    format='mp3',
                    acodec='mp3',
                    audio_bitrate=64000,
                )
                .run(overwrite_output=True)
            )
            #os.remove(TMP_DIR + self.name + TMP_EXT)
        except:
            return


class CbcPodcastRemake(PodcastRemake):

    def __init__(self, *args):
        super().__init__(*args)

    def dl(self, url = ''):
        try:
            # 1st dl: rss xml to determine target url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, timeout=10)
            next_url = re.search('https:.+\.mp3', r.text).group()
            # 2nd dl.: target media
            PodcastRemake.dl(self, next_url)
        except:
            return


PROVS_DICTS = (
    {
        'name': 'bbc',
        'origin_url':
            'https://www.bbc.co.uk/programmes/p002vsn1/episodes/player',
        'vol_level': 4,
    },
    {
        'name': 'cbc',
        'origin_url': 'https://www.cbc.ca/podcasting/includes/hourlynews.xml',
        'vol_level': 1,
    },
    #{
    #    'name': 'cbc',
    #    'origin_url': 'http://podcast.cbc.ca/mp3/hourlynews.mp3',
    #    'vol_level': 1,
    #},
    {
        'name': 'npr',
        'origin_url':
            'http://public.npr.org/anon.npr-mp3/npr/news/newscast.mp3',
        'vol_level': 1,
    },
)

for provs_dict in PROVS_DICTS:
    #cls = BbcPodcastRemake if provs_dict['name'] == 'bbc' else PodcastRemake
    if provs_dict['name'] == 'bbc':
        cls = BbcPodcastRemake  
    elif provs_dict['name'] == 'cbc':
        cls = CbcPodcastRemake  
    else:
        cls = PodcastRemake
    podcast_remake = cls(provs_dict)
    podcast_remake.dl(podcast_remake.origin_url)

