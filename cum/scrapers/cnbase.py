import re
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor

import requests
from snownlp import SnowNLP

from cum import config
from cum.scrapers.base import BaseChapter, BaseSeries

__all__ = ['build_download_pool', 'CNBaseSeries', 'BaseChapter']

HEAD = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64; rv:44.0) "
                   "Gecko/20100101 Firefox/44.0"),
}


def cn2pinyin(cn):
    return ' '.join(SnowNLP(cn).pinyin)


def gen_alias(cnstring):
    pinyin = cn2pinyin(cnstring)
    allowed_re = r'[A-Za-z0-9\-\s]'
    name = re.sub('-+', '-', pinyin.lower().replace(' ', '-'))
    return ''.join(c for c in name if re.match(allowed_re, c))


class HTTPUtil:
    CHARSET = 'utf-8'

    @classmethod
    def http_get(cls, url, **kwargs):
        if 'charset' in kwargs:
            charset = kwargs.get('charset')
            del kwargs['charset']
        else:
            charset = cls.CHARSET

        kwargs['headers'] = kwargs.get('headers', cls.build_headers())
        r = requests.get(url, **kwargs)
        r.encoding = charset
        return r

    @classmethod
    def build_headers(cls, **kwargs):
        return dict(HEAD, **kwargs)


def build_download_pool():
    return ThreadPoolExecutor(config.get().download_threads)


class CNBaseSeries(BaseSeries, HTTPUtil):

    @property
    def alias(self):
        return gen_alias(self.name)


class CNBaseChapter(BaseChapter, HTTPUtil):
    uses_pages = False

    @classmethod
    @abstractmethod
    def from_url(cls, url):
        """Method to initialize a Chapter object from the chapter URL."""
        raise NotImplementedError

    @staticmethod
    def page_download_finish(bar, files_queue, fs):
        """Callback functions for page_download_task futures, putting the
        resulting pairs of filehandle and its index to the queue and updating
        the progress bar.

        :param bar: ProgressBar
        :param fs: Future object contains task result
        :param files_queue: Queue object to store downloaded files' handles
        """
        files_queue.put(fs.result())
        bar.update(1)

    @staticmethod
    def queue2list(q):
        """Extract all items in a Queue into a list"""
        l = []
        for _ in range(0, q.qsize()):
            l.append(q.get())
        return l

    @classmethod
    def files_queue2sorted_list(cls, fq):
        """
        :type fq: queue.Queue[(int, T)]
        :rtype: list[T]
        """
        files_list = cls.queue2list(fq)
        files_list = sorted(files_list, key=lambda pair: pair[0])
        files_list = map(lambda pair: pair[1], files_list)
        return files_list
