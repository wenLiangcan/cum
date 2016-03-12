import zipfile
import imghdr
import io


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
