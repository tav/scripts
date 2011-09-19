#! /usr/bin/env python

from string import digits, letters
from random import choice

alphabet = letters + digits + '.-@/:?'

print ''.join(choice(alphabet) for i in range(20))
