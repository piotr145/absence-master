import unittest

from absence.generator.parser import LibrusParser


class TestLibrusParser(unittest.TestCase):
    def test_date_regex(self):
        regex = LibrusParser.date_re
        res = regex.match('2013-02-12 ')
        extr = [int(res.group(x)) for x in range(1, 4)]
        self.assertEqual(extr, [2013, 2, 12])

    def test_date_regex_wrong(self):
        regex = LibrusParser.date_re
        res = regex.match('qwe 2013-02-12 ')
        self.assertIsNone(res)
