# -*- coding: utf-8 -*-

from cum import config
import os
import tempfile
import unittest
import zipfile
import imghdr
import io
import re


class TestFuManHua(unittest.TestCase):
    FUMANHUA_URL = 'http://www.fumanhua.net/'

    def setUp(self):
        global fumanhua
        self.directory = tempfile.TemporaryDirectory()
        config.initialize(directory=self.directory.name)
        config.get().download_directory = self.directory.name
        from cum.scrapers import fumanhua

    def tearDown(self):
        self.directory.cleanup()

    def series_information_tester(self, data):
        URL = data['url']
        self.assertIsNotNone(re.match(fumanhua.FuManHuaSeries.url_re, URL))
        series = fumanhua.FuManHuaSeries(URL)
        self.assertEqual(series.name, data['name'])
        self.assertEqual(series.alias, data['alias'])
        self.assertEqual(series.url, URL)
        self.assertIsNone(series.directory)
        self.assertEqual(len(series.chapters), len(data['chapters']))
        for chapter in series.chapters:
            self.assertEqual(chapter.name, data['name'])
            self.assertEqual(chapter.alias, data['alias'])
            self.assertIn(chapter.chapter, data['chapters'])
            data['chapters'].remove(chapter.chapter)
            self.assertEqual(chapter.groups, [])
            self.assertIsNone(chapter.directory)
        self.assertEqual(len(data['chapters']), 0)

    def image_files_tester(self, zip_file_path, files_count):
        """Test images are downloaded correctly."""
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            files = zf.namelist()
            self.assertEqual(len(files), files_count)
            for f in files:
                with io.BytesIO(zf.read(f)) as img:
                    filetype = imghdr.what(img)
                    self.assertIsNotNone(filetype)
                    self.assertNotEqual(filetype, 'gif')

    def test_chapter_1_过剩妄想少年(self):
        URL = 'http://www.fumanhua.net/manhua/4701/567207.html'
        NAME = '过剩妄想少年'
        self.assertIsNotNone(re.match(fumanhua.FuManHuaChapter.url_re, URL))
        chapter = fumanhua.FuManHuaChapter.from_url(URL)
        self.assertEqual(chapter.alias, None)
        self.assertTrue(chapter.available())
        self.assertEqual(chapter.chapter, '1')
        self.assertIsNone(chapter.directory)
        self.assertEqual(chapter.groups, [])
        self.assertEqual(chapter.name, NAME)
        self.assertEqual(chapter.url, URL)
        self.assertEqual(chapter.title, '第1话')
        path_ = os.path.join(
            self.directory.name, NAME,
            '过剩妄想少年 - c001 [Unknown].zip'
        )
        self.assertEqual(chapter.filename, path_)
        chapter.download()
        self.image_files_tester(path_, 30)

    def test_series_过剩妄想少年(self):
        data = {
            'alias': 'guo-sheng-wang-xiang-shao-nian',
            'chapters': ['1', '2', '3', '4', '5', '番外1', '番外2'],
            'name': '过剩妄想少年',
            'url': 'http://www.fumanhua.net/manhua/4701/'
        }
        self.series_information_tester(data)

    def test_series_contains_only_one_chapter_部长比部下不足(self):
        data = {
            'alias': 'bu-chang-bi-bu-xia-bu-zu',
            'chapters': ['全一卷'],
            'name': '部长比部下不足',
            'url': 'http://www.fumanhua.net/manhua/4758/'
        }
        self.series_information_tester(data)


if __name__ == '__main__':
    unittest.main()
