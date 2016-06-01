# -*- coding: utf-8 -*-
"""Test all rulesets."""
import glob
import os
import subprocess
import unittest
import logging
import mock
from testfixtures import LogCapture

from lxml import etree

from ..oven import Oven

here = os.path.abspath(os.path.dirname(__file__))
TEST_RULESET_DIR = os.path.join(here, 'rulesets')
TEST_HTML_DIR = os.path.join(here, 'html')

logger = logging.getLogger('cnx-easybake')
logger.setLevel(logging.DEBUG)


def tidy(input_):
    """Pretty Print XHTML."""
    proc = subprocess.Popen(['{}/utils/xmlpp.pl'.format(here), '-sSten'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    output, _ = proc.communicate(input_)
    return output


def lessc(input_):
    """Convert less to css."""
    proc = subprocess.Popen(['lessc', '-'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    output, _ = proc.communicate(input_)
    return output

TEST_UUIDS = ["a321ce14-3b04-44ee-8fc2-7ec2e9e17906",
              "8e3fda66-929b-4688-98c3-5d37895bfded",
              "0e69e521-0a65-4a21-b685-1ae94cc2645e",
              "ee64a235-4f03-4eb2-885c-cbbd1dc5c666",
              "7b88db70-9f2e-4122-ac8d-d986698d8b98",
              "f67e4b94-ec19-46d4-927c-a809b03b39a1",
              "438e5b3b-5018-493b-80c1-5ce820d84e4e",
              "819c2122-aca7-43f6-af43-c5ee81febc80"
              ]


uuids = iter(TEST_UUIDS)


class RulesetTestCase(unittest.TestCase):
    """Ruleset test cases.

    Use easybake to transform <name>_raw.html with <name>.less and compare
    with <name>_cooked.html files
    """

    maxDiff = None

    def setUp(cls):
        """Setup logcap."""
        cls.logcap = LogCapture()

    def tearDown(cls):
        """Teardown logcap."""
        cls.logcap.uninstall()

    @classmethod
    def generate_tests(cls):
        """Build tests from css and html files."""
        for less_filename in glob.glob(os.path.join(TEST_RULESET_DIR,
                                       '*.less')):
            filename_no_ext = less_filename.rsplit('.less', 1)[0]
            header = []
            logs = []
            desc = None
            with open('{}.less'.format(filename_no_ext), 'rb') as f_less:
                for line in f_less:
                    if line.startswith('// '):
                        header.append(line[3:])
                    elif line.startswith('/'):
                        header.append(line[1:])
                f_less.seek(0)
                css_fname = '{}.css'.format(filename_no_ext)
                fnum = f_less.fileno()

                if not os.path.isfile(css_fname) or \
                   os.fstat(fnum).st_mtime > os.stat(css_fname).st_mtime:
                    with open(css_fname, 'wb') as f_css:
                        f_css.write(lessc(f_less.read()))

            if len(header) > 0:
                desc = header[0]

            test_name = os.path.basename(filename_no_ext)
            log_fname = '{}.log'.format(test_name)
            with open(os.path.join(TEST_HTML_DIR, log_fname), 'rb') as f_log:
                logs = (tuple(line[:-1].split(' ', 2)) for line in f_log)
                logs = tuple(logs)

            with open(os.path.join(TEST_HTML_DIR,
                                   '{}_cooked.html'.format(test_name)),
                      'rb') as f:
                cooked_html = tidy(f.read())

            with open(os.path.join(TEST_HTML_DIR,
                                   '{}_raw.html'.format(test_name)),
                      'rb') as f:
                html = f.read()

            setattr(cls, 'test_{}'.format(test_name),
                    cls.create_test('{}.css'.format(filename_no_ext),
                                    html, cooked_html, desc, logs))

    @classmethod
    def create_test(cls, css, html, cooked_html, desc, logs):
        """Create a specific ruleset test."""
        @mock.patch('cnxeasybake.oven.uuid4', uuids.next)
        def run_test(self):
            element = etree.HTML(html)
            oven = Oven(css)
            oven.bake(element)
            output = tidy(etree.tostring(element, method='html'))
            # https://bugs.python.org/issue10164
            self.assertEqual(output.split(b'\n'), cooked_html.split(b'\n'))
            if len(logs) == 0:
                self.logcap.check()
            else:
                self.logcap.check(*logs)

        if desc:
            run_test.__doc__ = desc
        return run_test


RulesetTestCase.generate_tests()
