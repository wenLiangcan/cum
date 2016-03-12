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
