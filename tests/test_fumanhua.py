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
        assert re.match(fumanhua.FuManHuaSeries.url_re, URL) is not None
        series = fumanhua.FuManHuaSeries(URL)
        assert series.name == data['name']
        assert series.alias == data['alias']
        assert series.url == URL
        assert series.directory is None
        assert len(series.chapters) == len(data['chapters'])
        for chapter in series.chapters:
            assert chapter.name == data['name']
            assert chapter.alias == data['alias']
            assert chapter.chapter in data['chapters']
            data['chapters'].remove(chapter.chapter)
            assert chapter.groups is []
            assert chapter.directory is None
        assert len(data['chapters']) == 0

    def image_files_tester(self, zip_file_path, files_count):
        """Test images are downloaded correctly."""
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            files = zf.namelist()
            assert len(files) == files_count
            for f in files:
                with io.BytesIO(zf.read(f)) as img:
                    filetype = imghdr.what(img)
                    assert filetype is not None
                    assert filetype != 'gif'

    def test_chapter_1_过剩妄想少年(self):
        URL = 'http://www.fumanhua.net/manhua/4701/567207.html'
        NAME = '过剩妄想少年'
        assert re.match(fumanhua.FuManHuaChapter.url_re, URL) is not None
        chapter = fumanhua.FuManHuaChapter.from_url(URL)
        assert chapter.alias == 'guo-sheng-wang-xiang-shao-nian'
        assert chapter.available() is True
        assert chapter.chapter == '1'
        assert chapter.directory is None
        assert chapter.groups is []
        assert chapter.name == NAME
        assert chapter.url == URL
        assert chapter.title == '第1话'
        path_ = os.path.join(
            self.directory.name, NAME,
            '过剩妄想少年 - c001 [Unknown].zip'
        )
        assert chapter.filename == path_
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
