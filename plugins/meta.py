#!/usr/bin/env python

from __future__ import print_function
import sys
import re

try:
    import urllib2
    import bs4 as BeautifulSoup
    
    _HAS_DEPS = True
    
    def ref_load(plugins):
        plugins.add_provider( HTMLMetaProvider() )
except:
    print("Missing deps for the HTML-meta parser")
    _HAS_DEPS = False

ignored_tags = set( ("reference", "author_institution", "publisher", "language",
                     "isbn", "issn", "pdf_url", "abstract_html_url")
               )

URL_PATTERN = "(^http[s]?://[\w.]*[.][\w]{2,6}(/.*)?)$"

class HTMLMetaProvider:
    "Find metadata in <meta> tags of web pages"
    
    def __init__(self):
        self.name = "meta"

    def load_ref(self, key):
        match = re.search(URL_PATTERN, key)
        if not match:
            return None
        
        url = match.groups()[0]
        try:
            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup.BeautifulSoup(html)
        except:
            return None
        
        if not soup.head:
            return
        
        metas = soup.head.findAll("meta")
        authors = []
        pages = ""
        links = {"url":url}
        ref = {"authors":authors, "links":links}
        missed = []
        for m in metas:
            if "name" not in m.attrs:
                continue
            
            name = m.attrs["name"]
            if name.startswith("citation"):
                name = name[9:]
                if name in ignored_tags:
                    continue
                
                value = m.attrs["content"]
                
                if name == "title":
                    ref["title"] = value
                elif name == "author":
                    author = prep_author(value)
                    if author:
                        authors.append(author)
                elif name == "publication_date" or name == "date":
                    ref["year"] = value.split("/")[0]
                elif name == "doi":
                    links["doi"] = value
                elif name == "pmid":
                    links["pmid"] = value
                elif name == "public_url":
                    links["url"] = value
                elif name == "firstpage":
                    pages = value
                elif name == "lastpage":
                    pages += "-"+value
                elif name == "volume":
                    ref["volume"] = value
                elif name == "issue":
                    ref["issue"] = value
                elif name == "journal_title":
                    ref["journal"] = value
                elif name == "inbook_title":
                    ref["journal"] = value
                elif name == "journal_abbrev":
                    if "journal" not in ref:
                        ref["journal"] = value
                else:
                    missed.append( (name, value) )
        
        if pages:
            ref["pages"] = pages
        
        if missed:
            print("Missed tags:")
            for m in missed:
                print(m)
            print()
        if len(authors) > 1 and "title" in ref:
            return ref
        
        return None


def prep_author(author):
    "Split a raw author name into lastname,givenname"
    
    d = author.split(" ")
    if len(d) < 2:
        return None
    
    if len(d) == 2:
        return d[1],d[0]
    
    idx = 1
    for v in d[1:-1]:
        l = len(v)
        if l < 2 or (l==2 and v[1] == "."):
            idx += 1
        else:
            break
    
    given = " ".join(d[:idx])
    last = " ".join(d[idx:])
    return last,given


def main(args):
    "Simple CLI to load a ref from a URL, using meta tags in the HTML header"
    
    if not _HAS_DEPS:
        print( "Missing dependencies, exiting" )
        return
    
    if len(args) != 2:
        print( "Usage: %s <ID>" % args[0] )
        print("The ID must be a URL")
        return
    
    key = args[1]
    provider = HTMLMetaProvider()
    print( provider.load_ref(key) )


if __name__ == "__main__":
    main( sys.argv )

