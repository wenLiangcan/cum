# -*- coding: utf-8 -*-

import re

from cum.scrapers.c99comic import C99ComicChapter, C99ComicSeries

__all__ = ['C99MangaChapter', 'C99MangaSeries']

CHARSET = 'gb2312'


class C99MangaChapter(C99ComicChapter):
    CHARSET = CHARSET
    url_re = re.compile(
        r'http://(?:dm\.)?99manga\.com/man/\d+/\d+\.htm\?s=\d+',
        re.IGNORECASE)

    DOMAIN = '99manga.com'
    PICLST_DECODE_KEY = 'gsanuxoewrm'

    @staticmethod
    def _extract_encoded_pic_list(html):
        list_re = re.compile(r'var\s+PicListUrl\s*=\s*"(.*?)";')
        return list_re.findall(html)[0]


class C99MangaSeries(C99ComicSeries):
    CHARSET = CHARSET
    url_re = re.compile(r'http://(?:dm\.)?99manga\.com/comic/\d+/',
                        re.IGNORECASE)

    CHAPTER = C99MangaChapter

    @property
    def name(self):
        name_re = re.compile(r'.*>>(.*)集数：.*')
        name_text = self.soup.find('div', class_='replo').text
        return name_re.findall(name_text)[0].strip()
