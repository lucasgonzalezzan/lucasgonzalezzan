import unittest

import myfiles.json_file_rw as io


class TestJson(unittest.TestCase):
    def test_read(self):
        """
        Test that we can open JSON files
        """
        file = "mytests/integration/fixtures/response.json"
        result = io.json_read(file)
        result = result['access_token']
        self.assertEqual(result, "VEtOLXJvYm90MDhkMTJlMzYtYjhhYi00MDYyLWE3NTEtNTg4NTgwOTIzMjE4")

class TestText(unittest.TestCase):
    def test_read(self):
        """
        Test that we can open text files
        """
        file = "mytests/integration/fixtures/response.json"
        result = io.file_lines(file)
        result = result[1]
        self.assertIn("access_token", result)  

class TestBin(unittest.TestCase):
    def test_read(self):
        """
        Test that we can open binary files
        """
        file = "mytests/integration/fixtures/response.json"
        result = io.bin_read(file)
        result = len(result)
        self.assertEqual(result, 228) 

    def test_read_Ogg_len(self): #IMP name = test*
        """
        Test that we can open Ogg files
        """
        file = "mytests/integration/fixtures/A_head.ogg"
        result = io.bin_read(file)
        result = len(result)
        self.assertEqual(result, 58)      
    def test_read_Ogg(self):
        """
        Read OggS bytes from the audio file
        """
        file = "mytests/integration/fixtures/A_head.ogg"
        result = io.bin_read(file)
        result = result[0:4]
        self.assertEqual(result, b'OggS')     