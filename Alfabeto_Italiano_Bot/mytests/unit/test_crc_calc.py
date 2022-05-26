import unittest

import myogg.mycrclib as mycrc


class TestOggCrc16(unittest.TestCase):
    def test_result(self):
        """
        Test that we can calc ogg pages CRC with 16bit tables
        """
        data = b'\x7f\xca\xfe\x42'
        result = mycrc.crc32ogg16(data)
        self.assertEqual(result, 0x1F2D6C1C)

    def test_bad_type(self):
        """
        Test bad inputs for Ogg CRC with 16bit tables
        """
        data = ("banana", 42, True, (1.0, 2.0) )
        for d in data:
            with self.assertRaises(TypeError) as cm:
                result = mycrc.crc32ogg16(d)

class TestOggCrc(unittest.TestCase):
    def test_result(self):
        """
        Test that we can calc ogg pages CRC
        """
        data = b'\x7f\xca\xfe\x42'
        result = mycrc.crc32ogg(data)
        self.assertEqual(result, 0x1F2D6C1C)

    def test_bad_type(self):
        """
        Test bad inputs for Ogg CRC
        """
        data = ("banana", 42, True, (1.0, 2.0) )
        for d in data:
            with self.assertRaises(TypeError) as cm:
                result = mycrc.crc32ogg(d) #