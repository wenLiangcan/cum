import os
import tempfile
import unittest

from common_testers import (image_files_tester, re_tester,
                            series_and_from_url_generated_chapter_equivalent_tester)
from cum import config


class TestC99Comic(unittest.TestCase):
    C99COMIC_URL = 'http://99comic.com/'

    def setUp(self):
        global c99comic
        self.directory = tempfile.TemporaryDirectory()
        config.initialize(directory=self.directory.name)
        config.get().download_directory = self.directory.name
        from cum.scrapers import c99comic

    def tearDown(self):
        self.directory.cleanup()

    def series_information_tester(self, data):
        url = data['url']
        self.assertIsNotNone(c99comic.C99ComicSeries.url_re.match(url))
        series = c99comic.C99ComicSeries(url)
        self.assertEqual(series.name, data['name'])
        self.assertEqual(series.alias, data['alias'])
        self.assertEqual(series.url, url)
        self.assertIsNone(series.directory)
        self.assertEqual(len(series.chapters), len(data['chapters']))
        for chapter in series.chapters:
            self.assertEqual(chapter.name, data['name'])
            self.assertEqual(chapter.alias, data['alias'])
            self.assertIn(chapter.chapter, data['chapters'])
            try:
                data['chapters'].remove(chapter.chapter)
            except ValueError as e:
                if not data.get('in_progress'):
                    raise e
            self.assertEqual(chapter.groups, [])
            self.assertIsNone(chapter.directory)
        self.assertEqual(len(data['chapters']), 0)

    def series_name_parsing_tester(self, series_url, name):
        series = c99comic.C99ComicSeries(series_url)
        self.assertEqual(series.name, name)
        for chapter in series.chapters:
            c = c99comic.C99ComicChapter.from_url(chapter.url)
            self.assertEqual(c.name, name)

    def series_chapter_num_tester(self, series_url, chapter_nums, in_progress=False):
        series = c99comic.C99ComicSeries(series_url)
        for chapter in series.chapters:
            self.assertIn(chapter.chapter, chapter_nums)
        if not in_progress:
            self.assertEqual(len(chapter_nums), len(series.chapters))
        else:
            self.assertLessEqual(len(chapter_nums), len(series.chapters))

    def chapter_chapter_num_tester(self, chapter_url, chapter_num):
        chapter = c99comic.C99ComicChapter.from_url(chapter_url)
        self.assertEqual(chapter.chapter, chapter_num)

    def series_generated_chapter_information_tester(self, chapter, data):
        self.assertEqual(chapter.url, data['url'])
        self.assertEqual(chapter.title, data['title'])

    def test_series_url_re(self):
        url = 'http://99comic.com/comic/9926756/'
        url_with_www = 'http://www.99comic.com/comic/9926756/'
        url_contains_capital_char = 'http://99comic.com/CoMic/9926756/'
        valid_urls = [url, url_with_www, url_contains_capital_char]

        url_invalid = 'http://99comi.com/CoMic/9926756/'
        invalid_urls = [url_invalid]

        re_tester(self, c99comic.C99ComicSeries.url_re, valid_urls, invalid_urls)

    def test_chapter_url_re(self):
        url = 'http://99comic.com/mh/9926756/list_228002.htm?s=10'
        url_with_www = 'http://www.99comic.com/mh/9926756/list_228002.htm?s=10'
        url_contains_capital_char = 'http://99comic.com/Mh/9926756/list_228002.htm?s=10'
        valid_urls = [url, url_with_www, url_contains_capital_char]

        invalid_urls = [
            'http://99comic.com/mh/9926756/list_228002.htm',
            'http://99comic.com/mh/9926756/list_228002.html?s=10',
            'http://99coic.com/mh/9926756/list_228002.htm?s=10'
        ]

        re_tester(self, c99comic.C99ComicChapter.url_re, valid_urls, invalid_urls)

    def test_chapters_generated_by_series_and_from_url_are_equivalent_十岁的保健体育(self):
        url = 'http://www.99comic.com/comic/9927699/'
        series_and_from_url_generated_chapter_equivalent_tester(self, url,
                                                                c99comic.C99ComicSeries,
                                                                c99comic.C99ComicChapter)

    def test_series_name_parsing_contains_spaces_GOODBYE_LILAC(self):
        self.series_name_parsing_tester('http://99comic.com/comic/9926575/',
                                        'GOODBYE LILAC')

    def test_series_成为世间的普通光景(self):
        data = {
            'in_progress': True,
            'alias': 'cheng-wei-shi-jian-de-pu-tong-guang-jing',
            'name': '成为世间的普通光景',
            'url': 'http://99comic.com/comic/9926756/',
            'chapters': [str(i).zfill(3) for i in range(1, 22)]
        }
        self.series_information_tester(data)

    def test_series_chapter_num_not_contained_number_绝热线上的悸动(self):
        url = 'http://www.99comic.com/comic/9916113/'
        chapter_nums = ['前篇', '后篇']
        self.series_chapter_num_tester(url, chapter_nums)

    def test_chapter_chapter_num_not_contained_number_绝热线上的悸动_前篇(self):
        url = 'http://www.99comic.com/mh/9916113/list_118705.htm?s=6'
        self.chapter_chapter_num_tester(url, '前篇')

    def test_chapter_chapter_num_contains_special_chars_十岁的保健体育_02卷番外(self):
        url = 'http://www.99comic.com/mh/9927699/list_226939.htm?s=3'
        self.chapter_chapter_num_tester(url, '02卷番外')

    def test_chapter_1_GOODBYE_LILAC(self):
        url = 'http://99comic.com/mh/9926575/list_194102.htm?s=10'
        name = 'GOODBYE LILAC'

        self.assertIsNotNone(c99comic.C99ComicChapter.url_re.match(url))
        chapter = c99comic.C99ComicChapter.from_url(url)
        self.assertEqual(chapter.alias, None)
        self.assertTrue(chapter.available())
        self.assertEqual(chapter.chapter, '001')
        self.assertIsNone(chapter.directory)
        self.assertEqual(chapter.groups, [])
        self.assertEqual(chapter.name, name)
        self.assertEqual(chapter.url, url)
        self.assertEqual(chapter.title, '001集')
        path_ = os.path.join(
            self.directory.name, name,
            '{} - c001 [Unknown].zip'.format(name)
        )
        self.assertEqual(chapter.filename, path_)
        chapter.download()
        image_files_tester(self, path_, 32)