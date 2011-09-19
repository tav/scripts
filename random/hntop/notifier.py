#! /usr/bin/env python

import sys

from datetime import datetime
from socket import setdefaulttimeout
from time import sleep
from traceback import print_exc

from feedparser import parse
from Growl import Image, GrowlNotifier

DEBUG = False

if sys.argv[1:]:
    DEBUG = True

def techcrunch(entry):
    text = entry.title + " " + entry.content[0].value
    text = text.lower()
    if 'facebook' in text:
        return 1
    if 'google' in text:
        return 1
    if 'apple' in text:
        return 1
    if 'steve jobs' in text:
        return 1
    if 'china' in text:
        return 1
    if 'y combinator' in text:
        return 1
    if 'amazon' in text:
        return 1
    if 'twitter' in text:
        return 1
    if 'android' in text:
        return 1
    if 'chrome' in text:
        return 1
    if 'foursquare' in text:
        return 1

sticky = True
icon = Image.imageFromPath('rss.png')

feeds = {
    "Aaron Swartz": ("http://www.aaronsw.com/weblog/index.xml", None, sticky),
    "A VC": ("http://feeds.feedburner.com/AVc", None, sticky),
    "catonmat": ("http://feeds.feedburner.com/catonmat", None, sticky),
    "Heroku": ("http://feeds.feedburner.com/heroku", None, sticky),
    "Jason Cohen": ("http://feeds2.feedburner.com/blogspot/smartbear", None, sticky),
    "John Gruber": ("http://daringfireball.net/feeds/articles", None, sticky),
    "John Resig": ("http://feeds.feedburner.com/JohnResig", None, sticky),
    # "Marco": ("http://www.marco.org/rss", None, sticky),
    # "Patrick": ("http://www.kalzumeus.com/feed/", None, sticky),
    "Paul Buchheit": ("http://paulbuchheit.blogspot.com/feeds/posts/default", None, sticky),
    "Paul Graham": ("http://www.aaronsw.com/2002/feeds/pgessays.rss", None, sticky),
    "Sivers": ("http://sivers.org/en.atom", None, sticky),
    "Steve Blank": ("http://steveblank.com/feed/", None, sticky),
    "Steve Yegge": ("http://steve-yegge.blogspot.com/feeds/posts/default", None, sticky),
    "TechCrunch": ("http://feeds.feedburner.com/TechCrunch", techcrunch, False),
    "Y Combinator": ("http://ycombinator.posterous.com/rss.xml", None, sticky),
    "Zed Shaw": ("http://zedshaw.com/feed.xml", None, sticky),
    }

notifier = GrowlNotifier('RSS', ['post'], applicationIcon=icon)
notifier.register()

virgin_run = True
cache = {}
recent = []

setdefaulttimeout(5)

while 1:
    for blog, (url, filter, stick) in feeds.items():
        print "=> %s [%s]" % (blog, datetime.now())
        try:
            feed = parse(url)
            if not hasattr(feed, 'status'):
                raise feed.bozo_exception
            if feed.status != 200:
                raise ValueError("Got %s for %s" % (feed.status, url))
            entries = feed['entries']
            if virgin_run:
                cache[blog] = blog_cache = set()
                for entry in entries:
                    blog_cache.add(entry.link)
                if DEBUG and entries:
                    entry = sorted(entries, key=lambda p: p.updated)[-1]
                    notifier.notify('post', blog, entry.title, sticky=False)
                    print
                    print "  ", entry.link
                    print
                    recent.append(entry.link)
            else:
                blog_cache = cache[blog]
                for entry in entries:
                    if entry.link not in blog_cache:
                        if filter:
                            try:
                                if not filter(entry):
                                    blog_cache.add(entry.link)
                                    continue
                            except Exception:
                                print
                                print_exc()
                                print
                        notifier.notify('post', blog, entry.title, sticky=stick)
                        print
                        print "  ", entry.link
                        print
                        recent.append(entry.link)
                        blog_cache.add(entry.link)
        except Exception:
            print
            print_exc()
            print
        if not virgin_run:
            sleep(10)
    if virgin_run:
        print
        print "Finished virgin run!"
    virgin_run = False
    print
    if recent:
        recent = recent[-10:]
        print '\n'.join(recent)
        print
    sleep(300)
