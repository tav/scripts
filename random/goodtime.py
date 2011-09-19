#! /usr/bin/env python

import re
import sys

from datetime import datetime
from time import sleep
from traceback import print_exc
from urllib import urlopen

LIMIT = 10

def get_data(path, type):
    hn = urlopen('http://news.ycombinator.com/' + path).read()
    timings = re.findall(r'> ([^<]*) ago  \| <a', hn)
    new_timings = []; add = new_timings.append
    for timing in timings:
        head, tail = timing.split()
        if 'minute' in tail:
            add(int(head))
        elif 'hour' in tail:
            add(int(head) * 60)
        elif 'day' in tail:
            add(int(head) * 60 * 24)
        else:
            raise ValueError("Unknown timing: %r" % timing)
    timings = ' '.join(map(str, new_timings))
    top = [x.split()[0] for x in re.findall('[0-9]+ point', hn)]
    listing = ' '.join(top)
    top = map(int, top)
    total1 = sum(top)
    total2 = sum(top[:LIMIT])
    print
    print "%s:" % type, listing
    print "Top %s:" % len(top), total1
    print "Top %s:" % LIMIT, total2
    print "Timings", timings
    print
    return total1, total2, listing, timings


def main(file=None):
    now = datetime.utcnow()
    print now
    fp_t1, fp_t2, fp_l, fp_a = get_data('news', "Frontpage")
    nl_t1, nl_t2, nl_l, nl_a = get_data('newest', "New Links")
    if file:
        file.write(
            'd %s %02d %02d t %02d %02d w %s '
            'ft %s %s nt %s %s fp %s np %s '
            'fa %s na %s\n'
            % (now.year, now.month, now.day, now.hour, now.minute,
               now.isoweekday(), fp_t1, fp_t2, nl_t1, nl_t2, fp_l, nl_l,
               fp_a, nl_a)
            )
        file.flush()

argv = sys.argv[1:]

if argv and argv[0] == 'run':
    file = open('.hn-data.txt', 'a')
    while 1:
        try:
            main(file)
        except Exception:
            print_exc()
        except KeyboardInterrupt:
            file.close()
            raise
        sleep(60 * 6)
else:
    main()
