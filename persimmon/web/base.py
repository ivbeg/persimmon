#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon basic classes for list handling
http://persimmon-project.org

Persimmon basic classes for list handling

"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"


import hashlib
from persimmon.web.consts import  PATH_TYPE_XPATH, TAGPATTERN_TYPE_LINEAR, TAG_KEY_ALLATTR


class DataSource:
    """Returns source of the data"""
    def __init__(self):
        pass



class ElementPath:
    """Path to the specified element"""
    def __init__(self, text, startKey = None, setKey=None, pathType=PATH_TYPE_XPATH, position=-1):
        self._pathType = PATH_TYPE_XPATH
        self._text = text
        self._startKey = startKey
        self._position = position
        self._setKey = setKey


def getNodeValue(node):
    """Returns string value of the node selected"""
#    print etree.tostring(node, pretty_print=True)
    text = ""
    for n in node.recursiveChildGenerator():
        if isinstance(n, str) and str(n.__class__).find("NavigableString") > -1:
            text += str(n)
        elif n.name == 'br':
            text += '\n' 
    return text.strip()



class TagPath:
    """Tag path class. Allows to create unique tag identification"""
    def __init__(self, node, limit=None):
        self.__shifts = []
        self.__tag_names = []
        self.limit = limit 
        
        self.__parseNode(node, limit)

    @staticmethod
    def getSharedNode(left, right, upToRelated=True):
        """Looks for shared parent for left and right nodes. upToRelated as True means using upper tag if shared tag is tbody"""
        l_path = TagPath(left)
        r_path = TagPath(right)
        change =  l_path.level - r_path.level
        p_1 = left.getparent()
        p_2 = right.getparent()
        if change > 0:
            for i in range(0, change):
                p_1 = p_1.getparent()
        elif change < 0:                 
            for i in range(0, change):
                p_2 = p_2.getparent()
        while p_1 is not None and p_2 is not None:
            if p_1 == p_2:
                if upToRelated and p_1.tag == 'tbody':
                    p_1 = p_1.getparent()
                return p_1
            p_1 = p_1.getparent()
            p_2 = p_2.getparent()
        return None
        
    @staticmethod
    def getSharedPath(left, right):
        """Returns node root for two other nodes"""
        node = TagPath.getSharedNode(left, right)
        if node:
            return TagPath(node)
        return None
    

    def __parseNode(self, node, limit, inprogress=False):
        """Parses node to the tag path"""
        parent = node.getparent()
        if parent is not None and parent.tag != '<DOCUMENT_ROOT>' and node != limit:
            self.__shifts.append(parent.index(node))
            self.__tag_names.append(node.tag)
            self.__parseNode(parent, limit, inprogress=True)
        else:
            self.__shifts.append(0)
            self.__tag_names.append(node.tag)           
        self.level = len(self.__shifts)            
        if not inprogress:
            self.__shifts.reverse()
            self.__tag_names.reverse()
        self.key = '_'.join(map(str, self.__shifts))
        md = hashlib.md5()
        md.update(self.key)
        self.hash = md.hexdigest()
         
    def __cmp__(self, tagpath):
        if list(self.values()) == list(tagpath.values()) and self.limit == tagpath.limit:
            return True
        return False
                
    def values(self):
        """Returns num of tag shifts"""
        return self.__shifts
    
    def key_values(self):
        """Returns list of values as unique key"""
        return '_'.join(map(str, self.__shifts))
    
    def tag_names(self):
        """Returns list of tag names"""
        return self.__tag_names
    
    def as_xpath(self):
        """Return path as xpath from root node"""
        tnames = self.__tag_names
#        tnames.reverse()
        vals = self.__shifts
#        vals.reverse()
        
        results = []
        i = 0
        results.append('//html')                 # lxml hack to support DOCUMENT_ROOT 
        for i in range(0, len(tnames)):
            results.append('/%s[%d]' %('*', vals[i] + 1))
            i += 1
        return ''.join(results)
    
class TagPattern:
    """Defines pattern created from group of html tags"""
    def __init__(self, ptype=TAGPATTERN_TYPE_LINEAR, elems = []):
        self.ptype = ptype
        self.__items = elems
        pass
    

    
class TagKey:
    """Unique key of tag on web page"""
    def __init__(self, node, params=[], exclude=[], useEmpty=False):
        self.node = node
        self.params = params
        self.exclude = exclude
        self.useEmpty = useEmpty
        self.key = self.getkey()
        pass    

    def getkey(self):
        """Returns key of selected tag key"""
        values = []
        if TAG_KEY_ALLATTR in self.params:
            for param in list(self.node.attrib.keys()):
                if param not in self.exclude:
                    values.append('%s=%s' %(param, self.node.attrib[param]))                
        else:
            for param in self.params:
                if param in self.node.attrib:
                    values.append('%s=%s' %(param, self.node.attrib[param]))
                elif self.useEmpty:
                    values.append('%s=%s' %(param, ""))
        if len(values) > 0:
            key = '%s[%s]' %(self.node.tag, '&'.join(values))
        else: 
            key = '%s' %(self.node.tag,)
        return key
    
    def __str__(self):
        return self.key
    
    def __unicode__(self):
        return self.key
    

class TagPatternBuilder:
    """Helps to create tag patterns"""
    def __init__(self):        
        pass
    
    def build(self, node):
        """Builds tag patterns by list"""
        names = []
        childs = node.getchildren()
        for ch in childs:
            key = TagKey(ch, [TAG_KEY_ALLATTR], exclude=['href'])
#            if type(key) != type(u""):
#                continue
            if len(names) == 0:
                names.append([key.key, 1])
            elif names[len(names)-1][0] == key.key:
                names[len(names)-1][1] += 1
            else:
                names.append([key.key, 1])
        return names

    def flatten_patterns(self, items):
        """Processes list of objects and converts it to the dictionary of object positions"""
        i = 0
        j = 0
        uniq = {}
        for i in range(0, len(items)):
            key = '_'.join(map(str, items[i]))
            if key not in list(uniq.keys()):
                uniq[key] = [i]
            else:            
                uniq[key].append(i)
        return uniq

    def process_patterns(self, ditems):
        """Processes dictionary of keyed tags positions and converts it to the dictionary of tag shifts"""
        uniq = {}
        for key in list(ditems.keys()):
            item = ditems[key]
            vals = []
            for i in range(0, len(item)):
                if i > 0:
                    vals.append(item[i] - item[i-1])
                else:
                    vals.append(0)
            uniq[key] = vals
        return uniq
            