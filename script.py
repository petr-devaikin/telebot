#!/usr/bin/env python2
# -*- coding: utf8 -*-
# vim:ts=4:sw=4


import cookielib, urllib2, sys

def doIt(uri):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    page = opener.open(uri)
    page.addheaders = [('User-agent', 'Mozilla/5.0')]
    print page.read()

for i in sys.argv[1:]:
    doIt(i)
