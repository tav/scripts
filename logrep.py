#! /usr/bin/env python

# Released into the Public Domain by tav <tav@espians.com>

"""
Logrep: Really Simple Apache Log Analysis Script

./logrep.py <logfile-pattern> [options]

  --vhost DOMAIN       Limit query to the specified domain.
  --filebase FILEBASE  The prefix for logfile-pattern if it's quoted.
  --ignore PATTERNS    Comma-separated list of patterns of URLS to ignore.
  -who                 Print the unique visitors (IP addresses).
  -where               Print the referring URLs.
  -what                Print the requested URLs.
  -total               Print the aggregate totals for who/where/what.
  -prune               Prune URLs to before the ?query_string part.
  -all                 Return all requests, not just those with status 200.
  --filter PATTERN     Return only requests which match the given pattern.

e.g. ./logrep.py access.2009-11-2[5-6]* --vhost tav.espians.com -prune --filter "/ciao*" -where -total

"""

import glob
import os
import sys

from collections import defaultdict
from fnmatch import fnmatch

__version__ = 3

# ------------------------------------------------------------------------------
# configure these to suit your log format
# ------------------------------------------------------------------------------

VHOST_POSITION = 0
IP_POSITION = 1
GET_POSITION = 7
HTTP_STATUS_POSITION = 9
REFERER_POSITION = 11
USER_AGENT_POSITION = 12

# ------------------------------------------------------------------------------
# settings
# ------------------------------------------------------------------------------

FILE_BASE = 'access.2009-'
IGNORE = ['/favicon.ico', '/robots.txt']

# ------------------------------------------------------------------------------
# utility funktions
# ------------------------------------------------------------------------------

def get_flag(flags, followed_by_value=True, default=None):
    """Return whether a specific flag is set in the command line parameters."""

    if not isinstance(flags, (list, tuple)):
        flags = [flags]

    argv = []
    retval = None
    sysargv = iter(sys.argv)
    while 1:
        try:
            arg = sysargv.next()
            retval_set = False
            for flag in flags:
                if arg == flag:
                    if followed_by_value:
                        retval = sysargv.next()
                    else:
                        retval = True
                    retval_set = True
            if not retval_set:
                argv.append(arg)
        except StopIteration:
            break
    sys.argv[:] = argv
    if retval is None:
        return default
    return retval

# ------------------------------------------------------------------------------
# kommand line given settings
# ------------------------------------------------------------------------------

if get_flag(('-h', '--help', '-help', 'help'), False):
    print __doc__
    sys.exit()

who = get_flag('-who', False)
where = get_flag('-where', False)
using = get_flag('-using', False)
what = get_flag('-what', False)
logline = get_flag(('-l', '-line'), False)
order = get_flag(('-o', '-order'), False)
total = get_flag(('-t', '-total'), False)
prune = get_flag(('-p', '-prune'), False)
all = get_flag(('-a', '-all'), False)
ignore = get_flag('--ignore', default=[])
vhost = get_flag('--vhost')
filter = get_flag('--filter')
where_filter = get_flag('--where-filter')
file_base = get_flag('--filebase', default=FILE_BASE)

if isinstance(ignore, str):
    ignore = ignore.split(',')

ignore.extend(IGNORE)

ignore = set(ignore)

# ------------------------------------------------------------------------------
# get the files to parse
# ------------------------------------------------------------------------------

given_files = sys.argv[1:]
files = []

for filename in given_files:
    if filename.endswith('*'):
        files += glob.glob(file_base+filename)
    else:
        files.append(filename)

files = sorted([filename for filename in files if os.path.isfile(filename)])

ips = set()
gets = defaultdict(int)
gets_ipset = defaultdict(set)
referers = defaultdict(int)
referers_ipset = defaultdict(set)
user_agents = defaultdict(int)
user_agents_ipset = defaultdict(set)

for filename in files:

    req = 0
    logfile = open(filename, 'rB')

    for line in logfile:

        log = line.split(' ')
        if vhost:
            if log[VHOST_POSITION] != vhost:
                continue
        if (not all) and log[HTTP_STATUS_POSITION] != '200':
            continue
        get = log[GET_POSITION]
        if get in ignore:
            continue
        ip = log[IP_POSITION]
        referer = log[REFERER_POSITION][1:-1]
        user_agent = ' '.join(log[USER_AGENT_POSITION:-1])[1:].split('"')[0]

        if not (who or where or what or using or logline):
            print ip, get, referer, user_agent
            continue

        if prune:
            get = get.split('?')[0]
            get = get.split('#')[0]
            referer = referer.split('?')[0]

        if who:
            if total:
                ips.add(ip)
            elif logline:
                print line
            else:
                print ip
            continue

        if what:
            if filter and not fnmatch(get, filter):
                continue
            if total:
                gets[get] += 1
                gets_ipset[get].add(ip)
            elif logline:
                print line
            else:
                print get
            continue

        if where:
            if filter and not fnmatch(get, filter):
                continue
            if where_filter and not fnmatch(referer, where_filter):
                continue
            if total:
                referers[referer] += 1
                referers_ipset[referer].add(ip)
            elif logline:
                print line
            else:
                print referer
            continue

        if using:
            # the filter here differs from what/where
            if filter and not fnmatch(get, filter):
                continue
            if total:
                user_agents[user_agent] += 1
                user_agents_ipset[user_agent].add(ip)
            else:
                print user_agent
            continue
            
    if not (who or where or what or using):
        continue

if not total:
    sys.exit()

def print_totals(ipset, raw):
    if order:
        total_count = sorted((v, k) for k, v in raw.items())
        for count, item in total_count:
            print count, '\t', len(ipset[item]), '\t', item
    else:
        total_count = sorted((len(v), k) for k, v in ipset.items())
        for count, item in total_count:
            print count, '\t', raw[item], '\t', item
    sys.exit()

if who:
    print len(ips)
    sys.exit()

if what:
    print_totals(gets_ipset, gets)

if where:
    print_totals(referers_ipset, referers)

if using:
    print_totals(user_agents_ipset, user_agents)
