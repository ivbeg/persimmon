#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon basic classes for list handling
http://persimmon-project.org

Persimmon mapper classes for list handling

"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"


import re
import time
import urllib.request, urllib.error, urllib.parse

import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from persimmon.web.base import getNodeValue
from persimmon.web.consts import *
from .bsoupxpath import Path
import logging


class BaseScheme:
    """Root scheme class"""

    def __init__(self):
        self.key_nodes = {}

    def getNode(self, document, epath):
        """Returns node by path"""
        node_path = Path(epath._text)
        node = document
        if epath._startKey is not None:
            if epath._startKey in self.key_nodes:
                node = self.key_nodes[epath._startKey]
        if epath._text is None and node != document:
            return node
        elems = node_path.apply(node)
        if len(elems) > 0:
            result = elems[0]
            if epath._setKey is not None:
                self.key_nodes[epath._setKey] = result
            return result
        return None


class BaseMapperScheme(BaseScheme):
    """Scheme of tag mapping to the scheme specified"""

    def __init__(self, schemeMap, schemeType, schemePath, rule_scheme=None, sub_schemes=None, keepRaw=True, limit=None):
        BaseScheme.__init__(self)
        self._map = schemeMap
        self._type = schemeType
        self._path = schemePath
        self._keepRaw = keepRaw
        self._limit = limit
        self._rule_scheme = rule_scheme
        self._sub_schemes = sub_schemes
        if self._rule_scheme:
            self._rule_scheme.setMapper(self)
        self.source = None

    def setSource(self, source):
        """Sets root source object"""
        self.source = source
        if self._sub_schemes:
            for key, scheme in list(self._sub_schemes.items()):
                scheme.setSource(source)

    def setParent(self, parent):
        """Sets parent mapper for this one"""
        self.parent_mapper = parent


class ComplexMapperScheme(BaseMapperScheme):
    """Complex scheme of tag mapping to the scheme specified"""

    def __init__(self, schemeMap, schemeType, schemePath, rule_scheme=None, keepRaw=True, limit=None):
        BaseMapperScheme.__init__(self, schemeMap, schemeType, schemePath, rule_scheme, keepRaw, limit)
        for key, mapper in self._map:
            mapper.setParent(self)

    def mapItem(self, root_node):
        """Maps item by collection of mappers"""
        item = {}
        for key, mapper in self._map:
            if mapper._type in [SCHEME_LIST_OBJECTS, SCHEME_LIST_TABLE]:
                item[key] = mapper.mapList(root_node)
            else:
                if key is None:
                    results = mapper.mapList(root_node)
                    if results:
                        item.update(results)
                else:
                    item[key] = mapper.mapList(root_node)
        return item


class MapperScheme(BaseMapperScheme):
    """Scheme of tag mapping to the scheme specified"""

    def __init__(self, schemeMap, schemeType, schemePath, rule_scheme=None, sub_schemes=None, keepRaw=True, limit=None,
                 row_shift=1):
        BaseMapperScheme.__init__(self, schemeMap, schemeType, schemePath, rule_scheme, sub_schemes, keepRaw, limit)
        self.__row_shift = row_shift
        if sub_schemes:
            for key, mapper in list(sub_schemes.items()):
                mapper.setParent(self)
                if self.source:
                    mapper.setSource(self.source)


    def mapField(self, field, node):
        """Maps HTML node to the selected field"""
        item = {}
        if node is None:
            return item
            #        print field
        #        print field._path
        if field._path is not None:
            n_path = Path(field._path._text)
            nodes = n_path.apply(node)
            if len(nodes) > 0:
                tag = nodes[0]
            else:
                return item
        else:
            tag = node
        if field._field_type == FIELD_TYPE_STRING:
            value = getNodeValue(tag)
            item[field._field_name] = value
            if item[field._field_name]:
                item[field._field_name] = item[field._field_name].strip()
        elif field._field_type == FIELD_TYPE_UINT32:
            try:
                value = int(tag.text)
            except:
                value = None
            item[field._field_name] = value
        elif field._field_type == FIELD_TYPE_DATE:
            value = getNodeValue(tag).strip()
            #            print 'DATE', tag, value
            item[field._field_name] = datetime.datetime.strptime(value, field._format)
        elif field._field_type == FIELD_TYPE_BOOLEAN:
            if tag.text in field._booleanmap:
                item[field._field_name] = field._booleanmap[tag.text]
            else:
                item[field._field_name] = None
        elif field._field_type == FIELD_TYPE_ATTRIBUTE:
        #            print etree.tostring(tag)
            item[field._field_name] = tag.attrs[field._attrname]
        elif field._field_type == FIELD_TYPE_URL:
            if 'href' in tag.attrs:
                if type(field._field_name) == type([]):
                    if field._field_name[0]:
                        item[field._field_name[0]] = getNodeValue(tag)
                    if field._field_name[1]:
                        item[field._field_name[1]] = tag.attrs['href']
                else:
                    item[field._field_name] = [tag.text, tag.attrs['href']]
            else:
                if type(field._field_name) == type([]):
                    for name in field._field_name:
                        item[name] = None
                else:
                    item[field._field_name] = None
        elif field._field_type == FIELD_TYPE_REGEXPMAP:
            values = field._regexp.search(tag.text)
            for key in field._fieldmap:
                value = values.group(key)
                if value:
                    item[key] = value
        return item

    def mapList(self, root_node):
        """Maps HTML block to the list of items"""
        if not root_node:
            return []
        if self._type == SCHEME_LIST_TABLE:
            results = []
            tbody_prefix = 'tbody/' if root_node.find('tbody') else ''
            #            if self.__row_shift != 0:
            #                node_path = Path(tbody_prefix + 'tr[position()>%d]' %(self.__row_shift))
            #            else:
            node_path = Path(tbody_prefix + 'tr')
            rows = node_path.apply(root_node)
            scheme = self._map
            n = 0
            r = rows[self.__row_shift:] if len(rows) > self.__row_shift else rows
            for row in r:
                n += 1
                node_path = Path('td')
                columns = node_path.apply(row)
                #columns = row.xpath('td')
                item = {}
                i = 0
                for col in columns:
                    field = scheme[i]
                    item.update(self.mapField(field, col))
                    tag = col
                    i += 1
                    if self._keepRaw:
                        pass
                        #                        item['__raw'] = etree.tostring(row, pretty_print=True)
                if self._rule_scheme:
                    item = self._rule_scheme.process(item)
                results.append(item)
                if self._limit and n == self._limit:
                    break
            return results
        elif self._type == SCHEME_LIST_OBJECTS:
            results = []
            node_path = Path(self._path._text)
            nodes = node_path.apply(root_node)
            #            nodes = root_node.xpath()
            #print self._path._text, nodes
            for node in nodes:
            #                print node
                item = {}
                for field in list(self._map.keys()):
                    item.update(self.mapField(self._map[field], node))
                    pass
                if self._rule_scheme:
                    item = self._rule_scheme.process(item)
                if self._sub_schemes:
                    for key, scheme in list(self._sub_schemes.items()):
                        item[key] = scheme.mapList(node)
                        #		print node
                if self._keepRaw:
                    item['__raw'] = str(node)
                    #	    	    for k in node:
                #	    	        print k.text
                results.append(item)
            return results
        return None

    def __clean_text(self, text):
        """Cleans texts
        :param text: text to clean
        """
        return text if not text else text.strip()

    def mapItem(self, root_node, cleanfunc=None):
        """Maps html block to selected item"""
        if self._type == SCHEME_TABLE_KEYVALUE:
            item = {}
            tbody_prefix = 'tbody/' if root_node.find('tbody') else ''
            node_path = Path(tbody_prefix + 'tr')
            rows = node_path.apply(root_node)
            #rows = root_node.xpath(tbody_prefix + 'tr[position()>1]')
            scheme = self._map
            for row in rows:
                row_path = Path('td')
                columns = row_path.apply(row)
                if len(columns) != 2:
                    continue
                if cleanfunc:
                    name = cleanfunc(columns[0].text)
                else:
                    name = self.__clean_text(columns[0].text)
                value_node = columns[1]
                if name in list(self._map.keys()):
                    field = self._map[name]
                    item.update(self.mapField(field, value_node))
                else:
                    logging.debug(('!! Name %s not found' % name))
            if self._sub_schemes:
                for key, scheme in list(self._sub_schemes.items()):
                    if key is not None:
                        item[key] = scheme.mapItem(root_node)
                    else:
                        item.update(scheme.mapItem(root_node))
            if self._rule_scheme:
                item = self._rule_scheme.process(item)
            if self._keepRaw:
                pass
                #                item['__raw'] = etree.tostring(root_node, pretty_print=True)
            return item
        elif self._type == SCHEME_ITEM_OBJECT:
            item = {}
            for field in list(self._map.keys()):
                item.update(self.mapField(self._map[field], root_node))
                pass
            if self._sub_schemes:
                for key, scheme in list(self._sub_schemes.items()):
                    if key is not None:
                        item[key] = scheme.mapItem(root_node)
                    else:
                        item.update(scheme.mapItem(root_node))
            if self._rule_scheme:
                item = self._rule_scheme.process(item)
            if self._keepRaw:
                pass
                #                item['__raw'] = etree.tostring(root_node, pretty_print=True)
            return item
        return None


class MapperField:
    """Defines field to map any unstructured data to the item field"""

    def __init__(self, name, field_name, field_type, unique=False, limit=1023, path=None):
        self._name = name
        self._field_name = field_name
        self._field_type = field_type
        self._limit = limit
        self._unique = unique
        self._path = path
        self._fields = {'name': name, 'field_name': field_name, 'field_type': field_type, 'limit': limit,
                        'unique': unique, 'path': None}


class RegexpMapField(MapperField):
    """Maps value from string using regular expression"""

    def __init__(self, name, field_name, regexp, fieldmap, path=None, unique=False):
        MapperField.__init__(self, name, field_name, FIELD_TYPE_REGEXPMAP, unique, path=path)
        self._regexp = regexp
        self._fieldmap = fieldmap
        self._fields['regexp'] = regexp
        self._fields['fieldmap'] = fieldmap


class DateMapperField(MapperField):
    """Maps string to the date value"""

    def __init__(self, name, field_name, unique=False, path=None, format='%d.%m.%Y'):
        MapperField.__init__(self, name, field_name, FIELD_TYPE_DATE, unique, path=path)
        self._format = format
        self._fields['format'] = format


class BooleanMapperField(MapperField):
    """Maps boolean attribute to value"""

    def __init__(self, name, field_name, unique=False, path=None, boolean_map=DEFAULT_BOOLEAN_MAP):
        MapperField.__init__(self, name, field_name, FIELD_TYPE_BOOLEAN, unique, path=path)
        self._booleanmap = boolean_map
        self._fields['booleanmap'] = boolean_map


class AttributeMapperField(MapperField):
    """Maps attribute to value"""

    def __init__(self, name, field_name, attrname, unique=False, path=None):
        MapperField.__init__(self, name, field_name, FIELD_TYPE_ATTRIBUTE, unique, path=path)
        self._attrname = attrname
        self._fields['attrname'] = attrname


class Pagination:
    """Pagination style"""

    def __init__(self, page_type=PAGE_TYPE_RANGE, pages=None, is_counted=False, page_len=None, start_empty=False,
                 num_shift=0):
        self.page_type = page_type
        self.pages = pages
        self.is_counted = is_counted
        self.page_len = page_len
        self.current_page = 0
        self.current_len = page_len
        self.start_empty = start_empty      # If set then first page has no key
        self.num_shift = num_shift          # Used to fix page number if it's not started from 1
        self.url = None

    def set_url(self, url):
        """Set url for pagination"""
        self.url = url

    def current(self):
        """Returns current page"""
        if self.page_type == PAGE_TYPE_RANGE:
            return str(self.pages[self.current])
        return None

    def currenturl(self):
        """Returns current page url"""
        if self.page_type == PAGE_TYPE_RANGE:
            return self.url % str(self.pages[self.current])
        return None


    def set_length(self, curlen):
        """Set current page length"""
        self.current_len = curlen

    def next(self, last_len=None):
        """Returns next page key. If last_len provided it used as last page length checker"""
        if last_len:
            self.set_length(last_len)

        result = None
        if self.page_type == PAGE_TYPE_RANGE:
            if len(self.pages) > self.current_page:
                result = str(self.pages[self.current_page])
        elif self.page_type == PAGE_TYPE_PAGED:
            if self.start_empty and self.current_page == 0:
                result = ''
            elif self.current_len == self.page_len:
                result = str(self.current_page + self.num_shift)
        elif self.page_type == PAGE_TYPE_COUNTED:
            if self.current_len == self.page_len:
                result = str(self.current_page * self.page_len)
        self.current_page += 1
        return result

    def nexturl(self, last_len=None):
        """Returns next page url"""
        page_num = self.next(last_len)
        if page_num is not None:
            url = self.url.replace('{{page}}', page_num)
            return url
        return None


class DoublePagination(Pagination):
    """Double pagination uses two iteration type of pagination"""

    def __init__(self, f_page_type=PAGE_TYPE_RANGE, f_pages=None, page_type=PAGE_TYPE_RANGE, pages=None,
                 is_counted=False, page_len=None, start_empty=False, num_shift=0):
        Pagination.__init__(self, page_type, pages, is_counted, page_len, start_empty, num_shift)
        self.f_page_type = f_page_type
        self.f_pages = f_pages
        self.f_current_page = 0

    def next(self, last_len=None):
        """Returns next page"""
        result = Pagination.next(self, last_len)
        if result:
            return result
        elif self.f_current_page < len(self.f_pages):
        #            print 'Fpages', self.f_current_page, len(self.f_pages)
            self.f_current_page += 1
            self.current_page = self.num_shift
            return self.current_page
        return None

    def nexturl(self, last_len=None):
        """Returns next page url"""
        page_num = self.next(last_len)
        #        print page_num, self.f_current_page
        if page_num is not None:
            if self.f_current_page < len(self.f_pages):
                url = self.url.replace('{{page}}', page_num)
                url = url.replace('{{f_page}}', str(self.f_pages[self.f_current_page]))
                return url
        return None


DEFAULT_ATTRS = {
    'encoding': 'utf-8',
    'limit': -1,
}


class MapRule:
    """Field mapping rule"""

    def __init__(self, key, to=None, type=RULE_TYPE_COPY):
        self.key = key
        self.to = to
        self.type = type
        pass


class RegexpMapRule(MapRule):
    """Field mapping rule based on regular expression"""

    def __init__(self, key, to, regexp):
        MapRule.__init__(self, key, to, type=RULE_TYPE_REGEXP)
        self.regexp = regexp
        self.re = re.compile(regexp)


class CopyFieldMapRule(MapRule):
    """Copy field to another field or list of fields"""

    def __init__(self, key, to):
        MapRule.__init__(self, key, to, type=RULE_TYPE_COPY)


class DeleteFieldMapRule(MapRule):
    """Delete field from item"""

    def __init__(self, key):
        MapRule.__init__(self, key, type=RULE_TYPE_DELETE)


class MergeFieldsMapRule(MapRule):
    """Rule map to merge fields of the item"""

    def __init__(self, key, to, area='source', pattern='', fields=[]):
        MapRule.__init__(self, key, to, type=RULE_TYPE_MERGEFIELDS)
        self.fields = fields
        self.pattern = pattern
        self.area = area


class RuleScheme:
    """Scheme to map item elements to other by rules"""

    def __init__(self, rules):
        self.rules = rules

    def setMapper(self, mapper):
        """Sets mapper object"""
        self.mapper = mapper

    def add_rule(self, rule):
        """Adds new rule"""
        self.rules.append(rule)

    def process(self, item):
        """Runs rules agains selected item"""
        for rule in self.rules:
            if rule.type == RULE_TYPE_REGEXP:               # Processes field using regular expression
                if rule.key in item:
                    value = item[rule.key]
                    m = rule.re.match(value)
                    if type(rule.to) == type([]):
                        for key in rule.to:
                            item[key] = m.group(key)
                    else:
                        result = m.group(rule.to)
                        item[rule.to] = result
            elif rule.type == RULE_TYPE_COPY:               # Processes field copy
                if rule.key in item:
                    value = item[rule.key]
                    if type(rule.to) == type([]):
                        for key in rule.to:
                            item[key] = value
                    else:
                        item[rule.to] = value
            elif rule.type == RULE_TYPE_DELETE:               # Processes field delete
                if rule.key in item:
                    del item[rule.key]
            elif rule.type == RULE_TYPE_MERGEFIELDS:        # Processes field merging
                if rule.key in item:
                    value = item[rule.key]
                    fields = [[rule.key, value]]
                    if rule.area == 'source':
                        source = self.mapper.source
                        for f in rule.fields:
                            if f in list(source.attrs.keys()):
                                fields.append([f, source.attrs[f]])
                    elif rule.area == 'item':
                        for f in rule.fields:
                            if f in list(item.keys()):
                                fields.append([f, item[f]])
                    pattern = rule.pattern
                    for key, value in fields:
                        if value:
                            pattern = pattern.replace('{' + key + '}', value)
                    if type(rule.to) == type([]):
                        for key in rule.to:
                            item[key] = pattern
                    else:
                        item[rule.to] = pattern
            elif rule.type == RULE_TYPE_ABSURLS:        # Replaces local urls with absolute urls
                # This rule is missing
                pass
        return item


class SourceScheme(BaseScheme):
    """Scheme to process data source to list of objects"""

    def __init__(self, attrs={}, pagination=None, lister={}, mapper=None):
        BaseScheme.__init__(self)
        self.attrs = DEFAULT_ATTRS.copy()
        self.attrs.update(attrs)
        self.lister = lister
        self.mapper = mapper
        self.pagination = pagination
        if self.mapper:
            self.mapper['scheme'].setSource(self)
        if self.lister:
            self.lister['scheme'].setSource(self)
        if self.pagination:
            self.pagination.set_url(attrs['url'])


    def fetch_url(self, url, timeout=2):
        """Fetches HTTP URL and returns it as StringIO"""
        #        print url
        time.sleep(timeout)
        f = urllib.request.urlopen(url)
        s = BytesIO(f.read())
        f.close()
#        f = open('last.html', 'w')
#        f.write(s.getvalue())
#        f.close()
        return s

    def getAttrs(self):
        """Return attributes"""
        return self.attrs

    def getLister(self):
        """Lister of the objects"""
        return self.lister


    def getItemByUrl(self, url):
        """Loads single item by url"""
        item = {}
        #        treebuilder = treebuilders.getTreeBuilder("etree", etree)
        #        p = html5parser.HTMLParser(tree=treebuilder, tokenizer=sanitizer.HTMLSanitizer)
        s = self.fetch_url(url)
        #        document = p.parse(s, encoding=self.attrs['encoding'])
#        document = fromstring(s)
        document = BeautifulSoup(s.read(), fromEncoding=self.attrs['encoding'])
        del s   # Clean immediately
        mapper = self.mapper['scheme']
        path = self.mapper['data_area_path']
        ipath = Path(mapper._path._text)
        elems = ipath.apply(document)
        table = elems[0]
        item = mapper.mapItem(table)
        return item

    def getitems(self, limit=None, useMapper=False):
        """Fetches objects from this data source"""
        #        treebuilder = treebuilders.getTreeBuilder("etree", etree)
        #       p = html5parser.HTMLParser(tree=treebuilder)#, tokenizer=sanitizer.HTMLSanitizer)
        items = []
        if useMapper and self.mapper:
            itemmapper = self.mapper['scheme']
        else:
            itemmapper = None
        if self.pagination:
            url = self.pagination.nexturl()
            while url is not None:
            #                print len(items)
                s = self.fetch_url(url)
                #                document = p.parse(s, encoding=self.attrs['encoding'])
                document = BeautifulSoup(s.read(), fromEncoding=self.attrs['encoding'])
                del s   # Clean immediately
                mapper = self.lister['scheme']
                data_area = self.getNode(document, self.lister['data_area_path'])
                #                print 'Data area', data_area
                n_items = mapper.mapList(data_area)
                if itemmapper is not None:
                    i = 0
                    for item in n_items:
                        item.update(self.getItemByUrl(item['url']))
                        i += 1
                        if limit and len(items) + i >= limit:
                            break
                items.extend(n_items)
                if limit and len(items) >= limit:
                    return items[:limit]
                else:
                    url = self.pagination.nexturl(len(n_items))
        else:
            url = self.attrs['url']
            s = self.fetch_url(url)
            document = BeautifulSoup(s.read(), fromEncoding=self.attrs['encoding'])
            mapper = self.lister['scheme']
            mapper.setSource(self)
            data_area = self.getNode(document, self.lister['data_area_path'])
            #if data_area:
            #    table = self.getNode(document, self.lister['scheme']._path)
            n_items = mapper.mapList(data_area)
            if itemmapper is not None:
                i = 0
                for item in n_items:
                    item.update(self.getItemByUrl(item['url']))
                    i += 1
                    if limit and len(items) + i >= limit:
                        break
            items.extend(n_items)
            if limit and len(items) >= limit:
                return items[:limit]
        return items
