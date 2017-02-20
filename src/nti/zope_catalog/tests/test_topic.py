#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import is_
from hamcrest import assert_that

from zope.index.topic.filter import PythonFilteredSet

from nti.zope_catalog.topic import TopicIndex
from nti.zope_catalog.topic import ExtentFilteredSet

from nti.zope_catalog.tests import SharedConfiguringTestLayer


class TestTopicIndex(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_apply_mixed_topics(self):
        # We can mix normal filtered sets and extent filtered sets
        # and query appropriately

        class Context(object):
            in_extent = False
            in_filter = False
            docid = None

            def __init__(self, in_extent=False, in_filter=False, docid=None):
                self.in_extent = in_extent
                self.in_filter = in_filter
                self.docid = docid

        extent = ExtentFilteredSet('extent', lambda _1, _2, x: x.in_extent)
        _filter = PythonFilteredSet('filter',
                                    'context.in_filter',
                                     family=extent.family)

        index = TopicIndex()
        index.addFilter(extent)
        index.addFilter(_filter)

        in_extent = Context(in_extent=True, docid=1)
        in_filter = Context(in_filter=True, docid=2)
        in_both = Context(in_extent=True, in_filter=True, docid=3)
        in_none = Context(docid=4)

        for x in in_extent, in_filter, in_both, in_none:
            index.index_doc(x.docid, x)

        assert_that(set(index['extent'].getIds()),
                    is_({1, 3}))

        assert_that(set(index['filter'].getIds()),
                    is_({2, 3}))

        assert_that(set(index.apply('extent')),
                    is_({1, 3}))
        assert_that(set(index.apply({'all_of': ['extent']})),
                    is_({1, 3}))
        assert_that(set(index.apply({'any_of': ['extent']})),
                    is_({1, 3}))

        assert_that(set(index.apply('filter')),
                    is_({2, 3}))
        assert_that(set(index.apply({'all_of': ['filter']})),
                    is_({2, 3}))
        assert_that(set(index.apply({'any_of': ['filter']})),
                    is_({2, 3}))

        assert_that(set(index.apply(['extent', 'filter'])),
                    is_({3}))
        assert_that(set(index.apply({'all_of': ['extent', 'filter']})),
                    is_({3}))
        assert_that(set(index.apply({'any_of': ['extent', 'filter']})),
                    is_({1, 2, 3}))

        # Take out in_extent
        in_extent.in_extent = False
        index.index_doc(in_extent.docid, in_extent)

        assert_that(set(index.apply(['extent', 'filter'])),
                    is_({3}))
        assert_that(set(index.apply({'all_of': ['extent', 'filter']})),
                    is_({3}))
        assert_that(set(index.apply({'any_of': ['extent', 'filter']})),
                    is_({2, 3}))

        # take out the one in both
        in_both.in_extent = False
        index.index_doc(in_both.docid, in_both)

        assert_that(set(index.apply(['extent', 'filter'])),
                    is_(set()))
        assert_that(set(index.apply({'all_of': ['extent', 'filter']})),
                    is_(set()))
        assert_that(set(index.apply({'any_of': ['extent', 'filter']})),
                    is_({2, 3}))
