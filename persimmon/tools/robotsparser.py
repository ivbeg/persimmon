# -*- coding: utf-8 -*-
"""Persimmon Crawler
http://persimmon-project.org

Persimmon Crawler fetches web pages as HTML and stores them in persistent storage

Persimmon Crawler works with Python 2.4 and up. It has no external
dependencies
"""


__author__ = "Ivan Begtin (ibegtin@gmail.com)"
__version__ = "3.0.4"
__copyright__ = "Copyright (c) 2008 Ivan Begtin"
__license__ = "Proprietary"

import sys

ROBOT_AGENT_PARAMS = ['crawl-delay', 'visit-time', 'request-rate']


class RobotsParser:
    """Class to parse robots.txt files"""
    def __init__(self, data):
        self.__raw = data
        self.__parts = {}
        self.__parse()

    def add_agent(self, useragent, disallow=None, allow=None, params=None):
        if not params: params = {}
        if not allow: allow = []
        if not disallow: disallow = []
        if 'agents' not in self.__parts:
            self.__parts['agents'] = {}
        self.__parts['agents'][useragent] = (disallow, allow, params)

    def set_host(self, hostname):
        self.__parts['hostname'] = hostname

    def add_unknown(self, line):
        if 'unknown' not in self.__parts:
            self.__parts['unknown'] = []
        self.__parts['unknown'].append(line)

    def add_sitemap(self, url):
        if 'sitemaps' not in self.__parts:
            self.__parts['sitemaps'] = []
        self.__parts['sitemaps'].append(url)

    def get_info(self):
        return self.__parts

    def is_allowed(self, agent, url):
        # TODO!
        if 'agents' not in self.__parts:
            for aname, values in list(self.__parts['agents'].items()):
                pass
        return True

    def write(self, fileobj):
        """Writes robots.txt to the file objects provided"""
        if 'agents' in self.__parts:
            for name, values in list(self.__parts['agents'].items()):
                fileobj.write('User-agent: %s\n' % name)
                for val in values[1]:
                    fileobj.write('Allow: %s\n' % (val))
                for val in values[0]:
                    fileobj.write('Disallow: %s\n' % val)
                for key, val in list(values[2].items()):
                    fileobj.write('%s: %s\n' % (key, val))
        if 'sitemaps' in self.__parts:
            for sm in self.__parts['sitemaps']:
                fileobj.write('Sitemap: %s\n' % sm)
        if 'hostname' in self.__parts:
            fileobj.write('Host: %s\n' % (self.__parts['hostname']))

    def __parse(self):
        lines = self.__raw.splitlines()
        current_agent = None
        for line in lines:
            line = line.decode('utf8').lstrip()
            if len(line) == 0 or line[0] == '#':
                continue
            pos = line.find('#')
            if pos > -1:
                line = line[:pos].strip()
            parts = line.split(':', 1)
            if len(parts) > 1:
                key = parts[0].lower()
                value = parts[1].strip()
                if key == 'host':
                    self.set_host(value)
                elif key == 'sitemap':
                    self.add_sitemap(value)
                elif key == 'user-agent':
                    if current_agent is not None:
                        self.add_agent(current_agent[0], current_agent[1], current_agent[2], current_agent[3])
                    current_agent = (value, [], [], {})
                elif key == 'disallow' and current_agent is not None:
                    current_agent[1].append(value)
                elif key == 'allow' and current_agent is not None:
                    current_agent[2].append(value)
                elif key in ROBOT_AGENT_PARAMS and current_agent is not None:
                    current_agent[3][key] = value
                else:
                    self.add_unknown(line)
            else:
                self.add_unknown(line)
        if current_agent is not None:
            self.add_agent(current_agent[0], current_agent[1], current_agent[2], current_agent[3])
        del lines


if __name__ == "__main__":
    from pprint import pprint
    import urllib.request, urllib.parse, urllib.error

    f = urllib.request.urlopen(sys.argv[1] + '/robots.txt')
    data = f.read()
    p = RobotsParser(data)
    pprint(p.get_info())
