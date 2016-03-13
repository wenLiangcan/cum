import imghdr
import io
import zipfile


def image_files_tester(test_case, zip_file_path, files_count):
    """Test images are downloaded correctly."""
    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        files = zf.namelist()
        test_case.assertEqual(len(files), files_count)
        for f in files:
            with io.BytesIO(zf.read(f)) as img:
                filetype = imghdr.what(img)
                test_case.assertIsNotNone(filetype)
                test_case.assertNotEqual(filetype, 'gif')


def re_tester(test_case, re_obj, valid_strings, invalid_strings):
    for vs in valid_strings:
        test_case.assertIsNotNone(re_obj.match(vs))
    for s in invalid_strings:
        test_case.assertIsNone(re_obj.match(s))


def series_and_from_url_generated_chapter_equivalent_tester(
        test_case, series_url, series_cls, chapter_cls):
    series = series_cls(series_url)
    for chapter in series.chapters:
        c = chapter_cls.from_url(chapter.url)
        test_case.assertEqual(chapter.name, c.name)
        test_case.assertEqual(chapter.title, c.title)
        test_case.assertEqual(chapter.chapter, c.chapter)


def series_name_parsing_tester(test_case, series_url, name,
                               series_cls, chapter_cls):
    """
    Test both series class and chapter class parsed series' name
    """
    series = series_cls(series_url)
    test_case.assertEqual(series.name, name)
    for chapter in series.chapters:
        c = chapter_cls.from_url(chapter.url)
        test_case.assertEqual(c.name, name)


def series_chapter_num_tester(test_case, series_url, chapter_nums,
                              series_cls, in_progress=False):
    """
    Test series class generated chapter objects' `chapter` attribute
    """
    series = series_cls(series_url)
    for chapter in series.chapters:
        test_case.assertIn(chapter.chapter, chapter_nums)
    if not in_progress:
        test_case.assertEqual(len(chapter_nums), len(series.chapters))
    else:
        test_case.assertLessEqual(len(chapter_nums), len(series.chapters))


def chapter_chapter_num_tester(test_case, chapter_url,
                               chapter_num, chapter_cls):
    """
    Test chapter object's `chapter` attribute
    """
    chapter = chapter_cls.from_url(chapter_url)
    test_case.assertEqual(chapter.chapter, chapter_num)
