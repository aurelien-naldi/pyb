#!/usr/bin/env python

from __future__ import print_function
import urllib2
import sys
from doi import get_doi
import re
import os

try:
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.latexenc import string_to_latex
    from bibtexparser.customization import *
    _HAS_DEPS = True
    
    def ref_load(plugins):
        provider = BiBTeXProvider()
        plugins.add_provider( provider )
        plugins.add_command(bibtex)
        plugins.add_importer("bib", provider)
except:
    print( "Missing deps for the bibtex provider" )
    _HAS_DEPS = False


meta2bibtex = (
    ("title","title"),
    ("journal","journal"),
    ("year","year"),
    ("volume","volume"),
    ("issue","number"),
    ("pages","pages"),
)

bibtex2meta = (
    ("year","year"),
    ("volume","volume"),
    ("number","issue"),
    ("pages","pages"),
)

class BiBTeXProvider:
    "Find metadata in the DOI system"
    
    def __init__(self):
        self.name = "doi"

    def load_ref(self, key):
        if key.endswith(".bib"):
            return self.load_bibtex(key)
        
        return self.load_doi(key)
    
    def load_doi(self, doi):
        "Create a ref based on a DOI, using the bibtex obtained from the DOI providers"
        
        doi = get_doi(doi)
        if not doi:
            return
        
        try:
            req = urllib2.Request("http://dx.doi.org/%s"%doi, headers = {'Accept' : 'application/x-bibtex'})
            bibtex = urllib2.urlopen(req).read().strip()
        except: bibtex = None
        
        # add fallback request to crossref API
        if bibtex is None:
            try:
                req = urllib2.Request("http://api.crossref.org/works/%s/transform/application/x-bibtex" % doi)
                bibtex = urllib2.urlopen(req).read().strip()
            except: bibtex = None
        
        if bibtex is None:
            return None
        
        ref = self.parse_bibtex(bibtex)
        
        # add the DOI link
        if "links" not in ref:
            ref["links"] = {"doi": doi}
        else:
            ref["links"]["doi"] = doi
        
        return ref

    def load_bibtex(self, key):
        "Create a ref from a bibtex file"
        f = open(key)
        result = parse_bibtex(f.read())
        f.close()
        return result

    def parse_bibtex_stream(self, bibtex):
        "Parse a bibtex entry (shared code between the load_bibtex and load_doi functions)"
        #print( bibtex )
        bp = BibTexParser(bibtex, customization=customize_bibtex)
        entries = bp.get_entry_list()
        return entries
        
    def parse_bibtex(self, bibtex):
        
        for b in self.parse_bibtex_stream(bibtex):
            return self.ref_from_bibtex(b)
        
        print( "WHAT?" )
    
    def ref_from_bibtex(self, b):
        title = b["title"]
        authors = [ [name.strip() for name in a.split(",")] for a in b["author"] ]
        if "journal" in b:
            journal = b["journal"]
        elif "booktitle" in b:
            journal = b["booktitle"]
        else:
            journal = ""
        ref = {
            "title": title,
            "authors": authors,
            "journal": journal
        }
        
        for bibtex_key, meta_key in bibtex2meta:
            if bibtex_key in b:
                ref[meta_key] = b[bibtex_key]
            
        return ref
    
    def import_file(self, path):
        print("Starting bibtex import...")
        f = open(path)
        bibtex = f.read()
        f.close()
        bib_refs = self.parse_bibtex_stream(bibtex)
        if not bib_refs:
            print("No parsed refs!")
            return []
        
        print("Converting parsed bibtex...")
        result = [ self.ref_from_bibtex(b) for b in bib_refs ]
        print("Done")
        return result


delkeys = ("abstract", "keywords")
def customize_bibtex(record):
    for k in delkeys:
        if k in record: del record[k]
    
    record = convert_to_unicode(record)
    record = author(record)
    
    # strip curly brackets
    for k in record:
        if k == "author":
            record[k] = [ re.sub(r'[{}]', '', a) for a in record[k] ]
            continue
        record[k] = re.sub(r'[{}]', '', record[k])
    return record


def bibtex(collection, args):
    """Save the list of stored references in the bibtex format
This will create/overwrite the 'exported_references.bib' file.
Provide another filename as argument to change the destination"""
    
    if len(args) > 1:
        print("Too many arguments")
        return
    if len(args) == 1:
        filename = args[0]
    else:
        filename = "exported_references.bib"
    
    f = open(filename, "w")
    for key in sorted(collection.get_references().keys()):
        ref = collection.get(key)
        f.write("%s\n\n" % to_bibtex(key,ref.get_meta()))
    f.close()


def to_bibtex(key, ref):
    # TODO: support other refs than article
    
    fields = []
    bib_authors = []
    for last,given in ref["authors"]:
        bib_authors.append( "%s, %s" % (last,given) )
    fields.append( ("author", " and ".join( bib_authors ) ) )
    
    # export many keys as is
    for meta_key, bibtex_key in meta2bibtex:
        if meta_key in ref:
            fields.append( (bibtex_key, ref[meta_key]) )
    
    if "links" in ref:
        for k,v in ref["links"].iteritems():
            fields.append( (k,v) )
    
    
    # build the bibtex snippet
    ret = "@article{%s" % key
    for k,v in fields:
        ret += ",\n  %s = {%s}" % (k,string_to_latex(v))
    ret += "\n}\n"
    return ret



def main(args):
    "Simple CLI to load a ref from a bibtex file (which can be retrieved from the DOI system)"
    
    if not _HAS_DEPS:
        print( "Missing dependencies, exiting" )
        return
    
    if len(args) != 2:
        print( "Usage: %s <ID>" % args[0] )
        print("The ID can be a doi or the name of a .bib file")
        return
    
    key = args[1]
    provider = BiBTeXProvider()
    print( provider.load_ref(key) )


if __name__ == "__main__":
    main( sys.argv )

