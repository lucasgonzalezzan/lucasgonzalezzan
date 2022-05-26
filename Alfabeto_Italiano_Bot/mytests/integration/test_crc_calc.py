import unittest

import myogg.mycrclib as mycrc
from myfiles.json_file_rw import bin_read as bin_read


class TestOggCrc(unittest.TestCase):
    def test_crc_Ogg(self):
        """
        Calc checksum for A_head.ogg audio file
        """
        file = "mytests/integration/fixtures/A_head_no_crc.ogg"
        data = bin_read(file)
        crc = mycrc.crc32ogg16(data)
        self.assertEqual(crc, 0x1AC94162) #ogg checksum is Least Significan Byte First 