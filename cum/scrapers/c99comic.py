# -*- coding: utf-8 -*-

import re
import urllib.parse as urlparse
from functools import partial
from queue import Queue

from bs4 import BeautifulSoup
from cum import config
from cum.scrapers.cnbase import CNBaseChapter, CNBaseSeries, download_pool

CHARSET = 'gb2312'


class C99ComicChapter(CNBaseChapter):
    CHARSET = CHARSET
    url_re = re.compile(
        r'http://(?:www\.)?99comic\.com/mh/\d+/list_\d+\.htm\?s=\d+',
        re.IGNORECASE)

    DOMAIN = '99comic.com'

    PIC_SERVERS = (
        "http://2.{}:9393/dm01/",
        "http://2.{}:9393/dm02/",
        "http://2.{}:9393/dm03/",
        "http://2.{}:9393/dm04/",
        "http://2.{}:9393/dm05/",
        "http://2.{}:9393/dm06/",
        "http://2.{}:9393/dm07/",
        "http://2.{}:9393/dm08/",
        "http://2.{}:9393/dm09/",
        "http://2.{}:9393/dm10/",
        "http://2.{}:9393/dm11/",
        "http://2.{}:9393/dm12/",
        "http://2.{}:9393/dm13/",
        "http://2.{}:9393/dm14/",
        "http://2.{}:9393/dm15/",
        "http://2.{}:9393/dm16/",
    )

    PICLST_DECODE_KEY = 'zhangxoewrm'

    def __init__(self, name=None, alias=None, chapter=None,
                 url=None, groups=None, title=None, directory=None):
        self.name = name
        self.alias = alias
        self.chapter = chapter
        self.url = url
        self.title = title
        self.directory = directory
        self.groups = groups or []

    @classmethod
    def from_url(cls, url):
        chapter_re = re.compile(r'([\.\d]+)[集卷]$')
        r = cls.http_get(url)
        soup = BeautifulSoup(r.text, config.get().html_parser)
        title_text = soup.find('title').text
        *name_parts, title, _, _ = title_text.split()
        name = ' '.join(name_parts).strip()
        chapter_parts = chapter_re.match(title)
        if chapter_parts:
            chapter = chapter_parts.group(1)
        else:
            chapter = title
        return cls(name=name, title=title, url=url, chapter=chapter)

    def download(self):
        html = self.http_get(self.url).text
        images = self._get_images(html)
        files_queue = Queue()
        with self.progress_bar(len(images)) as bar:
            with download_pool as pool:
                for i, img in enumerate(images):
                    r = self.http_get(img, stream=True)
                    fut = pool.submit(self.page_download_task, i, r)
                    fut.add_done_callback(partial(self.page_download_finish,
                                                  bar, files_queue))
            files_list = self.files_queue2sorted_list(files_queue)
            self.create_zip(files_list)

    def _get_images(self, html):
        server = self._get_pic_server()
        encoded_piclst = self._extract_encoded_pic_list(html)
        piclst = self._decode_piclst(encoded_piclst)
        return [server + p for p in piclst]

    def _get_pic_server(self):
        query = urlparse.urlparse(self.url).query
        server = urlparse.parse_qs(query)['s'][0]
        server = int(server) - 1
        return self.PIC_SERVERS[server].format(self.DOMAIN)

    @staticmethod
    def _extract_encoded_pic_list(html):
        list_re = re.compile(r'var\s+PicListUrls\s*=\s*"(.*?)";')
        return list_re.findall(html)[0]

    @staticmethod
    def _decode_piclst_base(encoded_lst, key, sep):
        for i, c in enumerate(key):
            encoded_lst = encoded_lst.replace(c, str(i))

        ss = encoded_lst.split(sep)
        return ''.join(map(chr, map(int, ss))).split('|')

    def _decode_piclst(self, encoded_lst):
        *key, sep = self.PICLST_DECODE_KEY
        return self._decode_piclst_base(encoded_lst, key, sep)


class C99ComicSeries(CNBaseSeries):
    CHARSET = CHARSET
    url_re = re.compile(r'http://(?:www\.)?99comic\.com/comic/\d+/',
                        re.IGNORECASE)
    CHAPTER = C99ComicChapter

    def __init__(self, url, directory=None):
        r = self.http_get(url)
        self.url = url
        self.directory = directory
        self.soup = BeautifulSoup(r.text, config.get().html_parser)
        self.chapters = self.get_chapters()

    @property
    def name(self):
        return self.soup.find(
            'meta', {'name': 'Keywords'}).attrs['content'].split(',')[0]

    def get_chapters(self):
        chapter_re = re.compile(r'.*?(([\.\d]+)[集卷])$')
        chapter_block = self.soup.select_one('.vol > .bl')
        chapter_list = [li.a for li in chapter_block.find_all('li')]

        chapters = []
        for item in chapter_list:
            url = urlparse.urljoin(self.url, item.attrs['href'])
            title_text = item.text
            title_parts = chapter_re.match(title_text)
            if title_parts:
                title = title_parts.group(1)
                chapter = title_parts.group(2)
            elif title_text.startswith(self.name):
                title = title_text.strip(self.name).strip()
                chapter = title
            else:
                *_, title = title_text.split()
                chapter = title
            c = self.CHAPTER(name=self.name, alias=self.alias,
                             chapter=chapter, url=url, title=title)
            chapters.append(c)
        return chapters
