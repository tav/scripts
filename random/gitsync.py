#! /usr/bin/env python

import sys

from commands import getoutput
from os import listdir
from subprocess import call
from time import sleep

BRANCH_MAP = {
  'default': 'hg'
  }

def run(*args):
    retcode = call(args)
    if retcode:
        sys.exit(1)

def main():
    """Update hg, export to git and push up references."""

    run('hg', 'pull', '-u')
    run('hg', 'gexport')

    branches = {}
    hg_heads = getoutput('hg branches --debug')

    for line in hg_heads.split('\n'):
        branch, rev = line.split()
        rev = rev.split(':')[1]
        branches[branch] = rev

    hg2git = {}
    mapfile = open('.hg/git-mapfile', 'rb')

    for line in mapfile:
        gitsha, hgsha = line.strip().split(' ', 1)
        hg2git[hgsha] = gitsha

    mapfile.close()

    git_branches = listdir('.hg/git/refs/heads')
    add = {}
    remove = set()

    for branch, hgsha in branches.iteritems():
        git_branch = BRANCH_MAP.get(branch, branch)
        add[git_branch] = hg2git[hgsha]

    for branch in git_branches:
        if branch not in add:
            remove.add(branch)

    if remove:
        for branch in remove:
            if branch in ('master', 'rebase', 'git-changes'):
                continue
            print "# Removing Branch:", branch
            run('git', '--git-dir=.hg/git', 'push', 'git@github-client:pypy/pypy.git', ':' + branch)

    print "# Updating Branches"
    for branch, id in add.iteritems():
        ref = open('.hg/git/refs/heads/' + branch, 'wb')
        ref.write(id + '\n')
        ref.close()
        run('git', '--git-dir=.hg/git', 'push', 'git@github-client:pypy/pypy.git', branch)

while 1:
    print "# Syncing"
    main()
    print "# Sleeping"
    sleep(60 * 10)
