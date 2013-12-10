from nose.tools import assert_equal, assert_not_equal, assert_raises, raises, with_setup
from nose.plugins.attrib import attr

from unittest import TestCase
import os, shutil
from GT.journal import Journal

with open('tests/data/correct_output.txt', 'r') as f:
    correct_output = ''.join(f.readlines())

with open('tests/data/correct_merge.txt', 'r') as f:
    correct_merge = ''.join(f.readlines())

with open('tests/data/two_days_correct.txt', 'r') as f:
    correct_twodays = ''.join(f.readlines())

with open('tests/data/2012-10-04.txt', 'r') as f:
    correct_04 = ''.join(f.readlines())

with open('tests/data/2012-10-05.txt', 'r') as f:
    correct_05 = ''.join(f.readlines())

class TestParsing(TestCase):
    def setUp(self):
        "set up test fixtures"
        shutil.copy("tests/data/tmp_journal.txt", "/tmp/journal.txt")

    def teardown(self):
        "tear down test fixtures"
        pass

    @attr('skip')
    def test_no_date(self):
        "try a file that has no datestamp whatsoever"
        "skipped because I don't know what the correct behaviour is"
        j = Journal("/tmp")
        j.parse("tests/data/no_date.txt")
        exported = j.export_week_old()
        assert exported

    @attr('skip')
    def test_almost_nothing(self):
        "test a file with almost nothing in it"
        "skipped because I don't know what the correct behaviour is"
        j = Journal("/tmp")
        j.parse("tests/data/almost_nothing.txt")
        exported = j.export_week_old("/tmp")
        assert exported

    def test_timestamp_ordering(self):
        "timestamps are not in the correct order; should warn about this"
        j = Journal("/tmp")
        j.parse("tests/data/out_of_order_times.txt")
        assert j.dump_day("2012-10-04")

    def test_merge(self):
        "combine two files with interwoven timestamps"
        j = Journal("/tmp")
        j.parse("tests/data/source_a.txt")
        j.parse("tests/data/source_b.txt")
        dumped = j.dump_day("2012-10-04")
        assert_equal(dumped, correct_merge)
    
    def test_tags(self):
        "ensure tags are parsed and preserved"
        j = Journal("/tmp")
        j.parse("tests/data/tags.txt")
        dumped = j.dump_day("2012-10-04")
        assert_equal(dumped, correct_output)

    def test_newlines(self):
        "see if a whole horde of weird newlines screws anything up"
        j = Journal("/tmp")
        j.parse("tests/data/excessive_newlines.txt")
        dumped = j.dump_day("2012-10-04")
        print dumped
        assert_equal(dumped, correct_output)

    def test_export(self):
        "make sure the exported file looks the way it should"
        j = Journal("/tmp/2d")
        j.parse("tests/data/two_days.txt")
        exported = j.export_week_old()
        assert exported

        with open('/tmp/2d/2012-10-04.txt', 'r') as f:
            check_04 = ''.join(f.readlines())

        with open('/tmp/2d/2012-10-05.txt', 'r') as f:
            check_05 = ''.join(f.readlines())

        assert_equal(correct_04, check_04)
        assert_equal(correct_05, check_05)

    def test_twodays(self):
        "ensure journals with several days in them continue to work"
        j = Journal("/tmp")
        j.parse("tests/data/two_days.txt")
        retained = j.get_recent_days(num_days = 100000)
        assert_equal(retained, correct_twodays)