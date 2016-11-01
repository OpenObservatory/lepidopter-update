import os
import re
import imp
import time
import operator
import multiprocessing

import unittest

UPDATERS_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', '..',
        'updater',
        'versions'
    )
)

UPDATER_FILE_REGEXP = re.compile(r"^update-(\d).py$")

class TestUpdaters(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("/etc/default/lepidopter"):
            raise RuntimeError("These must be run on a system that looks like lepidopter")

    def list_updaters(self):
        updaters = []
        for filename in os.listdir(UPDATERS_DIR):
            m = UPDATER_FILE_REGEXP.match(filename)
            if m:
                version = int(m.group(1))
                path = os.path.join(UPDATERS_DIR, filename)
                module = imp.load_source(
                    'updater_{0}'.format(version),
                    path
                )
                updaters.append({
                    'version': version,
                    'module': module,
                    'path': path
                })
        updaters.sort(key=operator.itemgetter('version'))
        return updaters

    def are_versions_consistent(self, updaters):
        last_version = 0
        for updater in updaters:
            # Ensure versions versions match the filename
            self.assertEqual(updater['module'].__version__,
                             str(updater['version']),
                             'Mismatch in __version__ variable of for updater-%s.py' % updater['version'])
            # Ensure versions always increase by one
            self.assertEqual(last_version + 1, updater['version'],
                             'Missing version %s' % last_version + 1)
            last_version = updater['version']

    def updaters_can_be_partial(self, updaters):
        for updater in updaters:
            p = multiprocessing.Process(target=updater['module'].run)
            p.start()
            time.sleep(0.5)
            p.terminate()

            p = multiprocessing.Process(target=updater['module'].run)
            p.start()
            p.join()
            self.assertEqual(p.exitcode, 0)

    def updaters_smoke_test(self, updaters):
        for updater in updaters:
            updater['module'].run()

    def test_update_lifecycle(self):
        updaters = self.list_updaters()
        self.are_versions_consistent(updaters)
        self.updaters_can_be_partial(updaters)
        self.updaters_smoke_test(updaters)

if __name__ == "__main__":
    unittest.main()
