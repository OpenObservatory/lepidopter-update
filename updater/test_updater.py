import os
import unittest

from updater import verify_file

CWD = os.path.dirname(__file__)

class TestSecurity(unittest.TestCase):
    def test_verify_file(self):
        o = verify_file(
            os.path.join(CWD, "versions", "update-1.py.asc"),
            os.path.join(CWD, "versions", "update-1.py"),
            os.path.join(CWD, "public.asc")
        )
        print o

if __name__ == "__main__":
    unittest.main()
