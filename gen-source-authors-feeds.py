#! /usr/bin/env python2.5

import urllib

from xml.etree import ElementTree as ET

# ------------------------------------------------------------------------------
# some konstants
# ------------------------------------------------------------------------------

NS = 'http://www.w3.org/2005/Atom'
LI = {'type': 'application/atom+xml', 'rel': 'self'}

ET._namespace_map[NS] = 'atom'

# ------------------------------------------------------------------------------
# da main funktion
# ------------------------------------------------------------------------------

def main(
    FEEDURL='http://source.plexnet.org/changesets.atom',
    PATH='http://source.plexnet.org/feeds/%s.atom',
    TITLE='Plexnet Source', FILEFMT='%s.atom'
    ):

    authors = {}
    feed = urllib.urlopen(FEEDURL)
    tree = ET.parse(feed).getroot()

    id = tree.find('{%s}id' % NS)
    link = tree.find('{%s}link' % NS)
    title = tree.find('{%s}title' % NS)
    updated = tree.find('{%s}updated' % NS)

    for entry in tree.findall('{%s}entry' % NS):
        author = entry.findtext('{%s}author/{%s}name' % (NS, NS))
        if author not in authors:
            sub = ET.Element(tree.tag, dict(tree.items()))
            sub.append(id)
            sub.append(link)
            LI['href'] = PATH % author
            sub.append(ET.Element(link.tag, LI))
            sub_title = ET.Element(title.tag)
            sub_title.text = TITLE # "%s by %s" % (title.text, author)
            sub.append(sub_title)
            sub.append(updated)
            authors[author] = [sub]
        authors[author].append(entry)

    gen = {}

    for author, elems in authors.items():
       root = elems.pop(0)
       for elem in elems:
          root.append(elem)
       root = ET.ElementTree(root)
       #out = open(FILEFMT % author, 'wb')
       #out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
       #out.write(ET.tostring(root))
       #out.close()
       root.write(FILEFMT % author, 'utf-8')

    index = open('index.html', 'wb')
    index.write(
        "<html><head><title>Plexnet Source &#187; Developer Activity Feeds"
        "</title></head><body><strong>Plexnet Source &#187; Developer Activity "
        "Feeds:</strong><ul>"
        )

    for author in sorted(authors):
        index.write(
            '<li><a href="/feeds/%s.atom">%s</a></li>' % (author, author)
            )
    
    index.write("</ul></body></html>")
    index.close()

# ------------------------------------------------------------------------------
# self runner
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
