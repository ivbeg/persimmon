#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
from urllib.request import urlopen
from bs4 import UnicodeDammit
from lxml.html import fromstring
import sys
#from persimmon.toolkit.lookweb.analyze import extract_menu


def decode_html(html_string):
        converted = UnicodeDammit(html_string, isHTML=True)
        if not converted.str:
                raise UnicodeDecodeError("Failed to detect encoding, tried [%s]", ', '.join(converted.triedEncodings))
        return converted.str


class PageExtractor:
    def __init__(self):
        pass

    def __get_page(self, url):
        realurl = None
        try:
            f = urlopen(url)
            data = f.read()
            realurl = f.geturl()
            f.close()
            root = fromstring(data)
        except KeyboardInterrupt:
            sys.exit(0)
#        try:
#            data = decode_html(data)
#        except TypeError:
#            return None, None
#        try:
#            root = fromstring(data)
#        except ValueError:
###            return None, None
        return root, realurl



    def extract_page_meta(self, url):
        BASE_KEYS = ['title', 'description', 'keywords', 'base','icon', 'styles', 'scripts', 'meta', 'feeds']
        results = {}
        for key in BASE_KEYS:
            results[key] = {'exists' : False, 'name' : key}
        root, real_url = self.__get_page(url)
        heads = root.xpath('//head')
        if len(heads) > 0:
            for tag in heads[0].getchildren():
                if tag.tag in ['title', 'description']:
                    results[tag.tag] = {'name' : 'title', 'exists' : True, 'value' : tag.text_content().strip()}
                elif tag.tag == 'base':
                    results[tag.tag] = {'name' : 'title', 'exists' : True, 'value' : tag.attrib['target'] if 'target' in tag.attrib else None}
                elif tag.tag == 'style':
                    if 'inlines' not in results['styles']:
                        results['styles']['inlines'] = []
                        results['styles']['exists'] = True
                    results['styles']['inlines'].append({'type' : tag.attrib['type'] if 'type' in tag.attrib else None, 'value' : tag.text_content()})
                elif tag.tag == 'meta':
                    if 'name' in tag.attrib:
                        name = tag.attrib['name'].lower().strip()
                        if name == 'description':
                            results['description'] = {'exists' : True, 'value' : tag.attrib['content'].strip(), 'name' : 'description'}
                        if name == 'keywords':
                            results['keywords'] = {'exists' : True, 'value' : tag.attrib['content'].strip(), 'name' : 'keywords'}
                        if 'named' not in results['meta']:
                            results['meta']['named'] = []
                            results['meta']['exists'] = True
                        results['meta']['named'].append({'name' : name, 'content' : tag.attrib['content'] if 'content' in tag.attrib  else None})
                    elif 'http-equiv' in tag.attrib:
                        name = tag.attrib['http-equiv'].lower()
                        if 'http-equiv' not in results['meta']:
                            results['meta']['http-equiv'] = []
                            results['meta']['exists'] = True
                        results['meta']['http-equiv'].append({'name' : name, 'content' : tag.attrib['content'] if 'content' in tag.attrib  else None})
                elif tag.tag == 'link':
                    if 'rel' in tag.attrib:
                        rel = tag.attrib['rel'].strip().lower()
                        if rel == 'stylesheet':
                            if 'refs' not in results['styles']:
                                results['styles']['refs'] = []
                                results['styles']['exists'] = True
                            results['styles']['refs'].append({'type' : tag.attrib['type'] if 'type' in tag.attrib else None, 'href' : tag.attrib['href']})
                        elif rel == 'alternative':
                            ttype = tag.attrib['type'].lower().strip()
                            if ttype == 'application/rss+xml':
                                if 'rss' not in results['feeds']:
                                    results['feeds']['rss'] = []
                                    results['feeds']['exists'] = True
                                results['feeds']['rss'].append({'type' : ttype, 'href' : tag.attrib['href']})
                            elif ttype == 'application/atom+xml':
                                if 'atom' not in results['feeds']:
                                    results['feeds']['atom'] = []
                                    results['feeds']['exists'] = True
                                results['feeds']['atom'].append({'type' : ttype, 'href' : tag.attrib['href']})
                        elif rel in ['icon', 'shortcut icon']:
                            results['icon'] = {'name' : 'icon', 'exists' : True, 'href' : tag.attrib['href']}
        return results

    def extract_simple_html_table(self, url, xpath, skip_top=1):
        bc = []
        pattern = re.compile(r'\s+')
        root, real_url = self.__get_page(url)
        objs = root.xpath(xpath)
        if not objs or len(objs) == 0:
            return
        table = objs[0]
        rows = table.xpath('tbody/tr')
        for row in rows[skip_top:]:
            rdata = []
            cols = row.xpath('td')
            for col in cols:
                text = re.sub(pattern, ' ', col.text_content().strip())
#                text = u''.join([e for e in col.recursiveChildGenerator() if isinstance(e,unicode)]).replace(u'\n', u' ').strip()
                rdata.append(text.encode('utf8'))
            empty = True
            for c in rdata:
                if len(c) > 0:
                    empty = False
                    break
            if empty: continue
            bc.append(rdata)
        results = {'num' : len(bc), 'list' : bc}
        return results


if __name__ == "__main__":
    ex = PageExtractor()
    #.extract_simple_html_table('http://nbfond.ru/konkurs-grantov/granty-2009/spisok-pobeditelej/', xpath="//table[@border='1']", skip_top=1)
#    data = ex.get_known_urls(sys.argv[1])
#    for r in data['known_urls']:
#        print r['text'], r['href']#, r['entities']
    data = ex.extract_page_meta(sys.argv[1])
    for r in list(data.values()):
        print(r)
