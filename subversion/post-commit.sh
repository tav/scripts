#!/bin/sh

# The post-commit hook is invoked after a commit.  Subversion runs
# this hook by invoking a program (script, executable, binary, etc.)
# named 'post-commit' (for which this file is a template) with the 
# following ordered arguments:
#
#   [1] REPOS-PATH   (the path to this repository)
#   [2] REV          (the number of the revision just committed)
#
# The default working directory for the invocation is undefined, so
# the program should set one explicitly if it cares.
#
# Because the commit has already completed and cannot be undone,
# the exit code of the hook program is ignored.  The hook program
# can use the 'svnlook' utility to help it examine the
# newly-committed tree.

REPOS="$1"
REV="$2"

cd /var/www/www.asktav.com/
touch regen
./post-commit-regen "$1" "$2" &

# /usr/share/subversion/hook-scripts/commit-email.pl "$REPOS" "$REV" developers@plexnet.org
