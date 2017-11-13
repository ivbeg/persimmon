#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import urllib.request, urllib.parse, urllib.error

from curl import Curl
import pycurl

import io

import http.client, urllib.parse

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'


def get_abs_url(root_url, url):
    """Returns absolute url"""
    https = False
    if root_url[:7] == 'http://':
        o = urllib.parse.urlparse(root_url)
    elif root_url[:8] == 'https://':
        o = urllib.parse.urlparse(root_url)
        https = True
    else:
        o = urllib.parse.urlparse('http://' + root_url)
        #    if url:
    #        o = urlparse.urlparse(root_url)
    if len(url) == 0:
        url = 'http://' + o.netloc
    if url[0] == '/':
        url = 'http://' + o.netloc + url
    elif url[:7] != 'http://' and url[:8] != 'https://':
        if len(o.path) > 0 and o.path[len(o.path) - 1] == '/':
            if o.path[len(o.path) - 1] == '/':
                url = root_url + url
            else:
                parts = o.path.rsplit('/', 1)
                if len(parts) == 1:
                    url = root_url + '/' + url
                else:
                    if not https:
                        url = 'http://' + o.netloc + parts[0] + '/' + url
                    else:
                        url = 'https://' + o.netloc + parts[0] + '/' + url

    return url


class HttpHeaders:
    """Class of HTTP headers"""

    def __init__(self, data):
        self.raw = data
        self.headers = HttpHeaders.headers_to_dict(data)


    def get_header(self, key):
        """Returns header"""
        if key in self.headers:
            return self.headers[key]
        return None


    def get_content_type(self):
        """Returns type of content"""
        result = self.get_header('content-type')
        if result:
            parts = result.split(';', 1)
            return parts[0].strip()
        return None

    @staticmethod
    def headers_to_dict(data):
        """Converts raw HTTP response to the dict of headers"""
        if not data:
            return {}
        lines = data.splitlines()
        result = {}
        #        parts = lines[0].split()
        #        result['__status'] = int(parts[1])
        #        result['__version'] = parts[0]
        #        result['__message'] = parts[2] if len(parts) > 2 else ""
        for line in lines[1:]:
            if len(line) > 0:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    name = parts[0].lower().strip()
                    value = parts[1].strip()
                    result[name] = value
                    if name == 'content-type':
                        parts = value.split(';')
                        result['__content_type'] = parts[0].strip()
                        if len(parts) > 1:
                            vals = parts[1].split('=')
                            name = vals[0].strip()
                            if name == 'charset' and len(vals) > 1:
                                result['__encoding'] = vals[1].lower().strip()
        return result


def fetch_url(url, nobody=0, timeout=30, follow_redirect=0, agent=USER_AGENT):
    """Fetch url using curl
    :param url:
    :param nobody:
    :param timeout:
    :param follow_redirect:
    :param agent:
    """
    t = io.StringIO()
    c = Curl()
    s = r"%s" % (url)
    c.set_option(pycurl.USERAGENT, agent)
    c.set_option(pycurl.URL, s.encode('utf-8'))
    c.set_option(pycurl.NOBODY, nobody)
    c.set_option(pycurl.FOLLOWLOCATION, follow_redirect)
    c.set_option(pycurl.WRITEFUNCTION, t.write)
    c.set_option(pycurl.TIMEOUT, timeout)
    attempt = 0
    try:
        c.get()
    except:
        return (None, None)
    return (c, t)


def fetch_url_headers(url):
    """Headers fetching using curl"""
    (resp, data) = fetch_url(url, nobody=1)
    if resp:
        return resp.header()
    return None


def fetch_url_headers2(url):
    """Alternative url fetching using httplib"""
    u = urllib.parse.urlparse(url)
    pyconn = http.client.HTTPConnection(u.netloc)
    path = u.path
    if u.query:
        path = path + '?' + u.query
    pyconn.request("HEAD", path)
    pyresp = pyconn.getresponse()
    headers = pyresp.msg
    adict = {'status': pyresp.status, 'version': pyresp.version, 'headers': headers.dict}
    return adict


def fetch_url_body2(url):
    """Simple http body fetching"""
    f = urllib.request.urlopen(url)
    data = f.read()
    f.close()
    return data


def fetch_url2(url):
    f = urllib.request.urlopen(url)
    data = f.read()
    headers = f.info()
    f.close()
    adict = {'status': f.status, 'version': f.version, 'headers': headers.dict, 'body': data}
    return adict


def fetch_url_body(url):
    (resp, data) = fetch_url(url, nobody=0)
    if data:
        return data.getvalue()
    return None
