# -*- coding: utf-8 -*-

"""
Tests specific to the Python based class lookup.
"""


import unittest, operator

from common_imports import etree, StringIO, HelperTestCase, fileInTestDir
from common_imports import SillyFileLike, canonicalize, doctest

from lxml.pyclasslookup import PythonElementClassLookup

xml_str = '''\
<obj:root xmlns:obj="objectified" xmlns:other="otherNS">
  <obj:c1 a1="A1" a2="A2" other:a3="A3">
    <obj:c2>0</obj:c2>
    <obj:c2>1</obj:c2>
    <obj:c2>2</obj:c2>
    <other:c2>3</other:c2>
    <c2>3</c2>
  </obj:c1>
</obj:root>'''


class PyClassLookupTestCase(HelperTestCase):
    """Test cases for the lxml.pyclasslookup class lookup mechanism.
    """
    etree = etree
    parser = etree.XMLParser()
    Element = parser.makeelement

    def tearDown(self):
        self.parser.setElementClassLookup(None)

    def _setClassLookup(self, lookup_function):
        class Lookup(PythonElementClassLookup):
            def lookup(self, *args):
                return lookup_function(*args)
        self.parser.setElementClassLookup( Lookup() )

    def _buildElementClass(self):
        class LocalElement(etree.ElementBase):
            pass
        return LocalElement

    def XML(self, xml):
        return self.etree.XML(xml, self.parser)

    # --- Test cases

    def test_lookup(self):
        el_class = self._buildElementClass()
        el_class.i = 1
        def lookup(*args):
            if el_class.i == 1:
                el_class.i = 2
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(2, el_class.i)

    def test_lookup_keep_ref_assertion(self):
        el_class = self._buildElementClass()
        el_class.EL = None
        def lookup(doc, el):
            if el_class.EL is None:
                el_class.EL = el
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, el_class.EL)
        self.assertRaises(AssertionError, el_class.EL.getchildren)

    def test_lookup_tag(self):
        el_class = self._buildElementClass()
        el_class.TAG = None
        def lookup(doc, el):
            if el_class.TAG is None:
                el_class.TAG = el.tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, root.TAG)
        self.assertEquals(root.tag, root.TAG)

    def test_lookup_text(self):
        el_class = self._buildElementClass()
        el_class.TEXT = None
        def lookup(doc, el):
            if el_class.TEXT is None:
                el_class.TEXT = el.text
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, root.TEXT)
        self.assertEquals(root.text, root.TEXT)

    def test_lookup_tail(self):
        el_class = self._buildElementClass()
        el_class.TAIL = None
        def lookup(doc, el):
            if el_class.TAIL is None:
                el_class.TAIL = el.tail
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(root.tail, root.TAIL)

    def test_lookup_attrib(self):
        el_class = self._buildElementClass()
        el_class.ATTRIB = None
        def lookup(doc, el):
            if el_class.ATTRIB is None:
                el_class.ATTRIB = el[0].attrib
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        items1 = root[0].attrib.items()
        items1.sort()
        items2 = root.ATTRIB.items()
        items2.sort()
        self.assertEquals(items1, items2)

    def test_lookup_prefix(self):
        el_class = self._buildElementClass()
        el_class.PREFIX = None
        def lookup(doc, el):
            if el_class.PREFIX is None:
                el_class.PREFIX = el.prefix
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(root.prefix, root.PREFIX)

    def test_lookup_sourceline(self):
        el_class = self._buildElementClass()
        el_class.LINE = None
        def lookup(doc, el):
            if el_class.LINE is None:
                el_class.LINE = el.sourceline
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(root.sourceline, root.LINE)

    def test_lookup_getitem(self):
        el_class = self._buildElementClass()
        el_class.CHILD_TAG = None
        def lookup(doc, el):
            el_class.CHILD_TAG = el[0].tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        child_tag = root.CHILD_TAG
        self.assertNotEquals(None, child_tag)
        self.assertEquals(root[0].tag, child_tag)

    def test_lookup_getitem_neg(self):
        el_class = self._buildElementClass()
        el_class.CHILD_TAG = None
        def lookup(doc, el):
            if el_class.CHILD_TAG is None:
                el_class.CHILD_TAG = el[-1].tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        child_tag = root.CHILD_TAG
        self.assertNotEquals(None, child_tag)
        self.assertEquals(root[-1].tag, child_tag)

    def test_lookup_getslice(self):
        el_class = self._buildElementClass()
        el_class.CHILD_TAGS = None
        def lookup(doc, el):
            if el_class.CHILD_TAGS is None:
                el_class.CHILD_TAGS = [ c.tag for c in el[1:-1] ]
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        child_tags = root.CHILD_TAGS
        self.assertNotEquals(None, child_tags)
        self.assertEquals([ c.tag for c in root[1:-1] ],
                          child_tags)

    def test_lookup_len(self):
        el_class = self._buildElementClass()
        el_class.LEN = None
        def lookup(doc, el):
            if el_class.LEN is None:
                el_class.LEN = len(el)
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(1, el_class.LEN)

    def test_lookup_bool(self):
        el_class = self._buildElementClass()
        el_class.TRUE = None
        def lookup(doc, el):
            if el_class.TRUE is None:
                el_class.TRUE = bool(el)
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assert_(el_class.TRUE)

    def test_lookup_get(self):
        el_class = self._buildElementClass()
        el_class.VAL = None
        def lookup(doc, el):
            if el_class.VAL is None:
                el_class.VAL = el[0].get('a1')
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, el_class.VAL)
        self.assertEquals(root[0].get('a1'), el_class.VAL)

    def test_lookup_get_default(self):
        el_class = self._buildElementClass()
        default = str(id(el_class))
        el_class.VAL = None
        def lookup(doc, el):
            if el_class.VAL is None:
                el_class.VAL = el[0].get('unknownattribute', default)
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(default, el_class.VAL)

    def test_lookup_getchildren(self):
        el_class = self._buildElementClass()
        el_class.CHILD_TAGS = None
        def lookup(doc, el):
            if el_class.CHILD_TAGS is None:
                el_class.CHILD_TAGS = [ c.tag for c in el.getchildren() ]
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        child_tags = root.CHILD_TAGS
        self.assertNotEquals(None, child_tags)
        self.assertEquals([ c.tag for c in root.getchildren() ],
                          child_tags)

    def test_lookup_getparent(self):
        el_class = self._buildElementClass()
        el_class.PARENT = None
        def lookup(doc, el):
            if el_class.PARENT is None:
                el_class.PARENT = el[0].getparent().tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertEquals(root.tag, root.PARENT)

    def test_lookup_getnext(self):
        el_class = self._buildElementClass()
        el_class.NEXT = None
        def lookup(doc, el):
            if el_class.NEXT is None:
                el_class.NEXT = el[0][1].getnext().tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, el_class.NEXT)
        self.assertEquals(root[0][1].getnext().tag, el_class.NEXT)

    def test_lookup_getprevious(self):
        el_class = self._buildElementClass()
        el_class.PREV = None
        def lookup(doc, el):
            if el_class.PREV is None:
                el_class.PREV = el[0][1].getprevious().tag
            return el_class
        self._setClassLookup(lookup)
        root = self.XML(xml_str)
        self.assertNotEquals(None, el_class.PREV)
        self.assertEquals(root[0][1].getprevious().tag, el_class.PREV)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(PyClassLookupTestCase)])
    return suite

if __name__ == '__main__':
    print 'to test use test.py %s' % __file__
