import os
import re
import tempfile
import unittest

from common_testers import (image_files_tester, re_tester,
                            series_and_from_url_generated_chapter_equivalent_tester,
                            series_name_parsing_tester)
from cum import config


class TestC99Mh(unittest.TestCase):
    C99MH_URL = 'http://99mh.com/'

    def setUp(self):
        global c99mh
        self.directory = tempfile.TemporaryDirectory()
        config.initialize(directory=self.directory.name)
        config.get().download_directory = self.directory.name
        from cum.scrapers import c99mh

    def tearDown(self):
        self.directory.cleanup()

    def series_information_tester(self, data):
        url = data['url']
        self.assertIsNotNone(c99mh.C99MhSeries.url_re.match(url))
        series = c99mh.C99MhSeries(url)
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

    def test_c99mhchapter_get_images(self):
        pic_link_re = re.compile(r'^http://images\.99mh\.com/dm\d\d/ok\-comic\d\d/.*$')
        url = 'http://99mh.com/comic/22822/232846/'
        chapter = c99mh.C99MhChapter(url=url)
        piclst = chapter._get_images(chapter.http_get(url).text)
        self.assertEqual(len(piclst), 37)
        for p in piclst:
            link_parts = pic_link_re.match(p)
            self.assertIsNotNone(link_parts)

    def test_series_url_re(self):
        url = 'http://99mh.com/comic/22822/'
        url_with_www = 'http://www.99mh.com/comic/22822/'
        url_contains_capital_chars = 'http://99mh.com/Comic/22822/'
        valid_urls = [url, url_with_www, url_contains_capital_chars]

        invalid_urls = [
            'http://99mh.com/comic/22822',
            'http://99h.com/comic/22822/',
            'http://99mh.com/comc/22822/',
            'http://99mh.com/comic/',
            'http://99mh.com/comic/22822/23323',
            'hhttp://99mh.com/comic/22822/'
        ]
        re_tester(self, c99mh.C99MhSeries.url_re, valid_urls, invalid_urls)

    def test_chapter_url_re(self):
        url = 'http://99mh.com/comic/22822/232846/'
        url_with_www = 'http://www.99mh.com/comic/22822/232846/'
        url_contains_capital_chars = 'http://99mh.com/Comic/22822/232846/'
        valid_urls = [url, url_with_www, url_contains_capital_chars]

        invalid_urls = [
            'http://99mh.com/comic/22822/',
            'http://99mh.com/comic/22822/232846',
            'http://99h.com/comic/22822/232846/',
            'http://99mh.com/cmic/22822/232846/',
            'http://99mh.com/comic/22822/232846/121213',
            'hhttp://99mh.com/comic/22822/232846/'
        ]
        re_tester(self, c99mh.C99MhChapter.url_re, valid_urls, invalid_urls)

    def test_chapters_generated_by_series_and_from_url_are_equivalent_zelo(self):
        url = 'http://99mh.com/comic/29590/'
        series_and_from_url_generated_chapter_equivalent_tester(self, url,
                                                                c99mh.C99MhSeries,
                                                                c99mh.C99MhChapter)

    def test_series_name_parsing_contains_spaces_LOVE_STRIKE(self):
        series_name_parsing_tester(self, 'http://99mh.com/comic/19774/',
                                   'LOVE STRIKE', c99mh.C99MhSeries,
                                   c99mh.C99MhChapter)

    def test_series_尘封的时光中(self):
        data = {
            'in_progress': True,
            'url': 'http://99mh.com/comic/28900/',
            'name': '尘封的时光中',
            'alias': 'chen-feng-de-shi-guang-zhong',
            'chapters': [str(i).zfill(3) for i in range(16)]
        }
        self.series_information_tester(data)

    def test_chapter_1_Zelo(self):
        url = 'http://99mh.com/comic/29590/232819/'
        name = 'Zelo'

        self.assertIsNotNone(c99mh.C99MhChapter.url_re.match(url))
        chapter = c99mh.C99MhChapter.from_url(url)
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
        image_files_tester(self, path_, 40)


if __name__ == '__main__':
    unittest.main()
