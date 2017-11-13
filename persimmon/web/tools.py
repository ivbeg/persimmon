#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persimmon web tools
http://persimmon-project.org

Persimmon web tools
"""


from lxml import etree

__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "1.0.1"
__copyright__ = "Copyright (c) 2017 Ivan Begtin"
__license__ = "BSD"

from persimmon.web.base import TagPath


def calculate_tag_stats(node):
    """Calculates tag statistics"""
    stats = {}
    for ch in node.getchildren():
        if ch.tag is etree.Comment:
            continue
        #        if type(ch.tag) != type(u""):
        #            continue
        if ch.tag not in list(stats.keys()):
            stats[ch.tag] = 0
        stats[ch.tag] += 1
        ch_stats = calculate_tag_stats(ch)
        for key in list(ch_stats.keys()):
            if key not in list(stats.keys()):
                stats[key] = ch_stats[key]
            else:
                stats[key] += ch_stats[key]
    return stats


def calculate_tag_stats_byattr(node, attr="class", stats={}, tags=[], tagattrs={}):
    """Calculates tag statistics
    :param node:
    :param attr:
    :param stats:
    :param tags:
    :param tagattrs:
    """
    for ch in node.getchildren():
        if ch.tag is etree.Comment:
            continue
        aval = ch.attrib[attr] if attr in ch.attrib else "None"
        tag = ch.tag
        if tag not in tags:
            tags.append(tag)
            tagattrs[tag] = [aval, ]
            stats[tag] = {aval: 1}
        else:
            if aval not in tagattrs[tag]:
                tagattrs[tag].append(aval)
                stats[tag][aval] = 1
            else:
                stats[tag][aval] += 1
        stats, tags, tagattrs = calculate_tag_stats_byattr(ch, attr, stats, tags, tagattrs)
    return stats, tags, tagattrs


def get_reversed_tag_path(node, limiter=None):
    """Returns reversed path to the selected node"""
    names = []
    names.append(node.tag)
    if node == limiter:
        return names
    parent = node.getparent()
    if parent:
        names.extend(get_reversed_tag_path(parent))
    return names


def find_2v_patterns(node):
    """Returns all vertical patterns of 2 elements"""
    patterns = {}
    for ch in node.getchildren():
        if type(node.tag) not in [type(""), type("")]:
            continue
        pattern = '%s/%s' % (node.tag, ch.tag)
        if pattern not in list(patterns.keys()):
            patterns[pattern] = 0
        patterns[pattern] += 1
        ch_stats = find_2v_patterns(ch)
        for key in list(ch_stats.keys()):
            if key not in list(patterns.keys()):
                patterns[key] = ch_stats[key]
            else:
                patterns[key] += ch_stats[key]
    return patterns


def find_v_patterns(node):
    """Returns all vertical patterns for selected node
    :param node:
    """
    patterns = {}
    path = TagPath(node)
    names = path.tag_names()
    names.reverse()
    l_n = len(names)
    for i in range(0, l_n - 1):
        pattern = '/'.join(names[i:])
        if pattern not in list(patterns.keys()):
            patterns[pattern] = 0
        patterns[pattern] += 1
    return patterns


def find_patterns(node, anum=2):
    """Returns all horisontal patterns of 2 elements"""
    patterns = {}
    last = None
    results = []
    for ch in node.getchildren():
        if ch.tag is not etree.Comment:
            results.append(ch)
    i = 0
    num = len(results)
    for i in range(0, num):
        ch = results[i]
        if num - i > (anum - 1):
            block = []
            for n in range(0, anum):
                block.append(results[i + n].tag)
            pattern = '/'.join(block)
            if pattern not in list(patterns.keys()):
                patterns[pattern] = 0
                patterns[pattern] += 1
    return patterns


def find_2h_patterns(node):
    """Returns all horisontal patterns of 2 elements"""
    patterns = {}
    last = None
    results = []
    for ch in node.getchildren():
        print(dir(ch))
        if ch.tag is not etree.Comment:
            results.append(ch)
    i = 0
    num = len(results)
    for i in range(0, num):
        ch = results[i]
        if num - i > 3:
            pattern = pattern = '%s/%s/%s/%s' % (
                results[i].name, results[i + 1].name, results[i + 2].name, results[i + 3].name)
            if pattern not in list(patterns.keys()):
                patterns[pattern] = 0
                patterns[pattern] += 1
            #        if last is not None:
            #            pattern = '%s/%s' %(last.tag, ch.tag)
            #            if pattern not in patterns.keys():
            #                patterns[pattern] = 0
            #                patterns[pattern] += 1
            #        ch_stats = find_2h_patterns(ch)
            #        for key in ch_stats.keys():
            #            if key not in patterns.keys():
            #                patterns[key] = ch_stats[key]
            #            else:
            #                patterns[key] += ch_stats[key]
            #       last = ch
    return patterns


if __name__ == "__main__":
    import sys
    from urllib.request import urlopen

    from lxml.html import etree

    parser = etree.HTMLParser()
    u = urlopen(sys.argv[1])
    soup = etree.fromstring(u.read(), parser=parser)
    patterns = calculate_tag_stats_byattr(soup, attr="id")[0]
    for n, p in list(patterns.items()):
        for k, v in list(p.items()):
            print(n, k, v)

