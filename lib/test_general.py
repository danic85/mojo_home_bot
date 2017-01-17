from general import time
import datetime
import unittest

class TestGeneralMethods(unittest.TestCase):

    def test_time(self):
        self.assertEqual(time(self), datetime.datetime.now().strftime('%I:%M %p'))

if __name__ == '__main__':
    unittest.main()