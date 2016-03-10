# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from cum import config
from cum.scrapers.base import BaseChapter, BaseSeries, download_pool
from urllib.parse import urljoin
from functools import partial
from queue import Queue
import re
import requests
from snownlp import SnowNLP

HEAD = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64; rv:44.0) "
                   "Gecko/20100101 Firefox/44.0"),
}
HTML_CHARSET = 'gb2312'


def cn2pinyin(cn):
    return ' '.join(SnowNLP(cn).pinyin)


def parse_chapter(title):
    chapter_re = re.compile(r'第(\d+)话|(番外\d+)')
    chapter_info = re.search(chapter_re, title)
    if not chapter_info:
        chapter = title
    else:
        chapter = chapter_info.group(1) or chapter_info.group(0)
    return chapter


def http_get(url, charset='utf-8', **args):
    r = requests.get(url, headers=HEAD, **args)
    r.encoding = charset
    return r


def queue2list(q):
    l = []
    for _ in range(0, q.qsize()):
        l.append(q.get())
    return l


class FuManHuaSeries(BaseSeries):
    url_re = re.compile(r'http://www\.fumanhua\.net/manhua/\d+/')

    def __init__(self, url, directory=None):
        r = http_get(url, charset=HTML_CHARSET)
        self.url = url
        self.directory = directory
        self.soup = BeautifulSoup(r.text, config.get().html_parser)
        self.chapters = self.get_chapters()

    @property
    def name(self):
        return self.soup.find('div', class_='title').h1.contents[0].string

    @property
    def alias(self):
        pinyin = cn2pinyin(self.name)
        allowed_re = r'[A-Za-z0-9\-\s]'
        name = re.sub('-+', '-', pinyin.lower().replace(' ', '-'))
        return ''.join(c for c in name if re.match(allowed_re, c))

    def get_chapters(self):
        chapter_list = [li.a
                        for li in self.soup.find(id='play_0').find_all('li')]
        chapters = []
        for item in chapter_list:
            url = urljoin(self.url, item.attrs['href'])
            title = item.attrs['title']
            chapter = parse_chapter(title)
            c = FuManHuaChapter(name=self.name, alias=self.alias,
                                chapter=chapter, url=url, title=title)
            chapters.append(c)
        return chapters


class FuManHuaChapter(BaseChapter):
    url_re = re.compile(r'http://www\.fumanhua\.net/manhua/\d+/\d+\.html')
    uses_pages = False

    pic_servers = ['http://pic.fumanhua.net',
                   'http://pic2.fumanhua.net']

    def __init__(self, name=None, alias=None, chapter=None,
                 url=None, title=None, directory=None, groups=None):
        self.name = name
        self.alias = alias
        self.chapter = chapter
        self.url = url
        self.title = title
        self.directory = directory
        self.groups = groups or []

    @staticmethod
    def from_url(url):
        page_title_re = re.compile(r'(.*)：(.*)\[.*')

        r = http_get(url, charset=HTML_CHARSET)
        soup = BeautifulSoup(r.text, config.get().html_parser)
        page_title = soup.find('title').string
        title_parts = re.search(page_title_re, page_title)
        name = title_parts.group(1)
        title = title_parts.group(2)
        chapter = parse_chapter(title)
        return FuManHuaChapter(name=name, chapter=chapter,
                               url=url, title=title)

    def download(self):
        r = http_get(self.url, charset=HTML_CHARSET)
        soup = BeautifulSoup(r.text, config.get().html_parser)
        pages = soup.find('select').find_all('option')
        images = self._parse_images(r.text, len(pages))
        referers = self._gen_referers(pages)
        files_queue = Queue()
        cookies = {
            'safedog-flow-item': '968D7BBF02E8B06CB31CF841061308EA'
        }
        with self.progress_bar(len(images)) as bar:
            with download_pool as pool:
                for i, img in enumerate(images):
                    headers = dict(HEAD, **{
                        'Referer': referers[i],
                        'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5'
                    })
                    r = requests.get(img, headers=headers, cookies=cookies,
                                     stream=True)
                    fut = pool.submit(self.page_download_task, i, r)
                    fut.add_done_callback(partial(self.page_download_finish,
                                                  bar, files_queue))
            files_list = queue2list(files_queue)
            files_list = sorted(files_list, key=lambda pair: pair[0])
            files_list = map(lambda pair: pair[1], files_list)
            self.create_zip(files_list)

    def _get_pic_server(self, i):
        return self.pic_servers[i % len(self.pic_servers)]

    def _gen_referers(self, pages):
        pages = sorted(pages, key=lambda p: int(p.string))
        page_ids = map(lambda item: item.attrs['value'], pages)
        referers = map(lambda id_: urljoin(self.url, '{}.html'.format(id_)),
                       page_ids)
        return list(referers)

    def _parse_images(self, html, pages_count):
        img_re = re.compile(r"var imgurl = '(.*)';")
        link = img_re.findall(html)[0]
        img_path, filename = link.rsplit('/', 1)
        start_id, ext = filename.split('.')
        id_len = len(start_id)
        start_id = int(start_id)

        images = []
        for i in range(pages_count):
            id_ = str(start_id + i).rjust(id_len, '0')
            img = urljoin(self._get_pic_server(i),
                          '{}/{}.{}'.format(img_path, id_, ext))
            images.append(img)
        return images

    @staticmethod
    def page_download_finish(bar, files_queue, fs):
        """Callback functions for page_download_task futures, assigning the
        resulting filehandles to the right index in the array and updating
        the progress bar.
        """
        files_queue.put(fs.result())
        bar.update(1)
