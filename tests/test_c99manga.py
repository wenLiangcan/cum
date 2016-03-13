import os
import re
import tempfile
import unittest

from common_testers import (chapter_chapter_num_tester, image_files_tester,
                            re_tester,
                            series_and_from_url_generated_chapter_equivalent_tester,
                            series_chapter_num_tester,
                            series_name_parsing_tester)
from cum import config


class TestC99Manga(unittest.TestCase):
    C99MANGA_URL = 'http://99manga.com/'

    def setUp(self):
        global c99manga
        self.directory = tempfile.TemporaryDirectory()
        config.initialize(directory=self.directory.name)
        config.get().download_directory = self.directory.name
        from cum.scrapers import c99manga

    def tearDown(self):
        self.directory.cleanup()

    def series_information_tester(self, data):
        url = data['url']
        self.assertIsNotNone(c99manga.C99MangaSeries.url_re.match(url))
        series = c99manga.C99MangaSeries(url)
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

    def test_c99mangachapter_get_images(self):
        pic_link_re = re.compile(r'^http://2\.99manga\.com:9393/dm(\d\d)//.*$')
        url = 'http://dm.99manga.com/man/22987/225094.htm?s=7'
        chapter = c99manga.C99MangaChapter(url=url)
        server_count = len(chapter.PIC_SERVERS)
        piclst = chapter._get_images(chapter.http_get(url).text)
        self.assertEqual(len(piclst), 40)
        for p in piclst:
            link_parts = pic_link_re.match(p)
            self.assertIsNotNone(link_parts)
            self.assertLessEqual(int(link_parts.group(1)), server_count)

    def test_series_url_re(self):
        url = 'http://99manga.com/comic/22987/'
        url_with_dm = 'http://dm.99manga.com/comic/22987/'
        url_contains_capital_chars = 'http://99manga.com/Comic/22987/'
        valid_urls = [url, url_with_dm, url_contains_capital_chars]

        invalid_urls = [
            'http://www.99manga.com/comic/22987/',
            'http://dm.99manga.com/comic/22987',
            'http://99comic.com/comic/22987/',
        ]
        re_tester(self, c99manga.C99MangaSeries.url_re,
                  valid_urls, invalid_urls)

    def test_chapter_url_re(self):
        url = 'http://99manga.com/man/22987/225094.htm?s=7'
        url_with_dm = 'http://dm.99manga.com/man/22987/225094.htm?s=7'
        url_contains_capital_chars = 'http://99manga.com/Man/22987/225094.htm?s=7'
        valid_urls = [url, url_with_dm, url_contains_capital_chars]

        invalid_urls = [
            'http://99manga.com/man/22987/225094.htm',
            'http://dm.99manga.com/man/22987/225094.html?s=7',
            'http://99manga.com/mh/22987/225094.htm?s=7',
            'http://99manga.com/man/225094.htm?s=7'
        ]
        re_tester(self, c99manga.C99MangaChapter.url_re,
                  valid_urls, invalid_urls)

    def test_chapters_generated_by_series_and_from_url_are_equivalent_和煦阳光和便当男孩(self):
        url = 'http://dm.99manga.com/comic/22987/'
        series_and_from_url_generated_chapter_equivalent_tester(self, url,
                                                                c99manga.C99MangaSeries,
                                                                c99manga.C99MangaChapter)

    def test_series_name_parsing_contains_spaces_遥之天穹_景月传(self):
        url = 'http://dm.99manga.com/comic/27386/'
        name = '遥之天穹 景月传'
        series_name_parsing_tester(self, url, name, c99manga.C99MangaSeries,
                                   c99manga.C99MangaChapter)

    def test_series_chapter_num_not_contained_number_太喜欢你妄想漫游(self):
        url = 'http://dm.99manga.com/comic/24744/'
        chapter_nums = ['前篇']
        series_chapter_num_tester(self, url, chapter_nums, c99manga.C99MangaSeries,
                                  in_progress=True)

    def test_chapter_chapter_num_not_contained_number_太喜欢你妄想漫游_前篇(self):
        url = 'http://dm.99manga.com/man/24744/176405.htm?s=10'
        chapter_chapter_num_tester(self, url, '前篇', c99manga.C99MangaChapter)

    def test_series_黑猫和侯爵的侍者(self):
        data = {
            'in_progress': True,
            'alias': 'hei-mao-huo-hou-jue-de-shi-zhe',
            'name': '黑猫和侯爵的侍者',
            'url': 'http://dm.99manga.com/comic/28242/',
            'chapters': [str(i).zfill(3) for i in range(1, 4)]
        }
        self.series_information_tester(data)

    def test_chapter_2_HANGER执行人(self):
        url = 'http://dm.99manga.com/man/24499/174612.htm?s=11'
        name = 'HANGER执行人'

        self.assertIsNotNone(c99manga.C99MangaChapter.url_re.match(url))
        chapter = c99manga.C99MangaChapter.from_url(url)
        self.assertEqual(chapter.alias, None)
        self.assertTrue(chapter.available())
        self.assertEqual(chapter.chapter, '002')
        self.assertIsNone(chapter.directory)
        self.assertEqual(chapter.groups, [])
        self.assertEqual(chapter.name, name)
        self.assertEqual(chapter.url, url)
        self.assertEqual(chapter.title, '002集')
        path_ = os.path.join(
            self.directory.name, name,
            '{} - c002 [Unknown].zip'.format(name)
        )
        self.assertEqual(chapter.filename, path_)
        chapter.download()
        image_files_tester(self, path_, 31)


if __name__ == '__main__':
    unittest.main()
