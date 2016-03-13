# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
import string
import urllib.parse as urlparse
from cum import config

from cum.scrapers.c99comic import C99ComicChapter, C99ComicSeries

__all__ = ['C99MhChapter', 'C99MhSeries']

CHARSET = 'uft-8'

chapter_re = re.compile(r'.*?(([\.\d]+)[集卷])$')


def parse_title_chapter(series_name, title_text):
    chapter_parts = chapter_re.match(title_text)
    if chapter_parts:
        title = chapter_parts.group(1)
        chapter = chapter_parts.group(2)
    elif title_text.startswith(series_name):
        title = title_text[len(series_name):].strip()
        chapter = title
    else:
        *_, title = title_text.split()
        chapter = title

    return title, chapter


class C99MhChapter(C99ComicChapter):
    CHARSET = CHARSET
    url_re = re.compile(r'^http://(?:www\.)?99mh\.com/comic/\d+/\d+/$',
                        re.IGNORECASE)

    @classmethod
    def from_url(cls, url):
        r = cls.http_get(url)
        soup = BeautifulSoup(r.text, config.get().html_parser)
        name = soup.find('span', {'id': 'spt1'}).text.strip()
        title_text = soup.find('span', {'id': 'spt2'}).text.strip()
        # chapter_parts = chapter_re.match(title_text)
        title, chapter = parse_title_chapter(name, title_text)
        # if chapter_parts:
        #     title = chapter_parts.group(1)
        #     chapter = chapter_parts.group(2)
        # elif title_text.startswith(name):
        #     title = title_text[len(name):].strip()
        #     chapter = title
        # else:
        #     *_, title = title_text.split()
        #     chapter = title
        return cls(name=name, title=title, chapter=chapter, url=url)

    @staticmethod
    def _extract_encoded_pic_list(html):
        list_re = re.compile(r'var\s+sFiles\s*=\s*"(.*?)";')
        return list_re.findall(html)[0]

    def _get_pic_server(self):
        server_host = 'http://images.99mh.com/'
        server_re = re.compile(r'var\s+sPath\s*=\s*"(.*?)";')
        html = self.http_get(self.url).text
        server = server_re.findall(html)[0]
        return urlparse.urljoin(server_host, server)

    def _decode_piclst(self, encoded_lst):
        d = string.ascii_lowercase.index(encoded_lst[-1]) + 1
        lst_len = len(encoded_lst)
        e = encoded_lst[lst_len - d - 12:lst_len - d - 1]
        new_lst = encoded_lst[0:lst_len - d - 12]
        *key, sep = e
        return self._decode_piclst_base(new_lst, key, sep)


class C99MhSeries(C99ComicSeries):
    CHARSET = CHARSET
    url_re = re.compile(r'^http://(?:www\.)?99mh\.com/comic/\d+/$',
                        re.IGNORECASE)
    CHAPTER = C99MhChapter

    @property
    def name(self):
        return self.soup.find(
            'span', {'class': 'cActBarTitle'}).contents[-1].strip(' >\r\n')

    def get_chapters(self):
        chapter_list = self.soup.select_one('#subBookListAct').find_all('a')
        chapters = []
        for item in chapter_list:
            url = item.attrs['href']
            title_text = item.text
            title, chapter = parse_title_chapter(self.name, title_text)
            c = self.CHAPTER(name=self.name, alias=self.alias,
                             chapter=chapter, title=title, url=url)
            chapters.append(c)
        return chapters
