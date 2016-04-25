#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from lxml import html

def parse(page, prefix):
    result = []

    doc = pq(html.fromstring(page))
    items = doc('.contentBlock table.td_chromed')

    for item in items:
        info = {}

        header = item[0][0]
        description = item[0][1]

        header_links = pq(header)('a')

        info['href'] = prefix + header_links[0].get('href')
        info['name'] = header_links[0][0].text

        meta = pq(item)('table table td')

        img = pq(meta[0])('img')
        if img:
            info['img'] = prefix + img[0].get('src').replace('thumbnails', 'fullsize')


        info['logo'] = meta[1][1].text.strip().encode('utf-8')
        info['location'] = meta[2][1].text.strip().encode('utf-8')
        info['color'] = meta[3][1].text.strip().encode('utf-8')
        info['tested'] = meta[4][1].text.strip().encode('utf-8')
        info['shape'] = meta[5][1].text.strip().encode('utf-8')
        info['content'] = meta[6][1].text.strip().encode('utf-8')
        info['report_quality'] = meta[7][1].text.strip().encode('utf-8')
        info['rating'] = meta[8][1].text.strip().encode('utf-8')
        info['warning'] = meta[9][1].text.strip().encode('utf-8')

        result.append(info)

    return result
