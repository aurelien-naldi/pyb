#!/usr/bin/env python

from __future__ import print_function
import unicodedata
import json
import os

def debug(*l):
    if False:
        print(*l)

OFIELDS = ("title", "authors", "year", "journal", "volume", "issue", "pages", "links")
FIELDS = set( OFIELDS )


class Ref:
    """Store all metadata about a reference.
    It is the central representation of a reference, which can be
    created from multiple sources and saved in multiple formats.
    """
    
    def __init__(self, meta):
    
        # add selected fields as attributes
        self.extra = []
        self.missed = []
        for key in meta.keys():
            value = meta[key]
            if key in FIELDS:
                setattr(self, key, value)
            else:
                self.missed.append((key,value))
        
        # default for missing fields
        for key in FIELDS:
            if not hasattr(self, key):
                setattr(self, key, None)
        
        # Remove the ending point which is often included
        if self.title.endswith("."):
            self.title = self.title[:-1]
        
        if not self.links:
            self.links = {}
        
        self.tags = set()
        self.alternatives = []
    
    def add_alternative(self, ref):
        self.alternatives.append(ref)
    
    def add_link(self, key, value):
        "Add an identifier to this reference (pubmed, doi)"
        self.links[key] = value
    
    def add_tag(self, tag):
        self.tags.add(tag)
    
    def short(self):
        descr = u"%s\n%s (%s)" % (self.title, self.fmt_authors(), self.year)
        return descr.encode("utf-8")
    
    def __str__(self):
        issue = ""
        if self.volume:
            if self.issue:
                issue = "%s(%s):" % (self.volume, self.issue)
            else:
                issue = "%s:" % self.volume
        elif self.issue:
            issue = "%s:" % self.issue
        descr = u"%s\n%s (%s)\n%s %s%s\n%s" % (self.title, self.fmt_authors(), self.year, self.journal, issue, self.pages, self.links)
        return descr.encode("utf-8")
    
    def fmt_authors(self):
        "Get a formatted list of authors"
        authors = self.authors
        if len(self.authors) > 7:
            authors = authors[:5]
            authors.append(("et al.", ""))
        return ", ".join( [ self.fmt_author(a) for a in authors ] )
    
    def fmt_author(self, author):
        lastName, givenName = author
        return "%s %s" % (lastName, givenName)
    
    def get_meta(self):
        meta = {}
        for key in FIELDS:
            value = getattr(self, key)
            if value:
                meta[key] = value
        return meta
    
    def encode(self, encoder):
        ret = "{\n"
        isfirst = True
        for key in OFIELDS:
            value = getattr(self,key)
            if value:
                if isfirst:
                    isfirst = False
                else:
                    ret += ",\n"
                
                ret += '"%s": %s' % (key, encoder.encode(value))
        ret += "\n}\n"
        return ret

class RefCollection:
    def __init__(self):
        self.refs = {}
        self.path = "references.json"
        if os.path.isfile(self.path):
            f = open(self.path)
            rawrefs = json.load(f)
            f.close()
            
            for k in rawrefs.keys():
                r = rawrefs[k]
                self.add_reference(Ref(r))
    
    def add_reference(self, ref, key=None):
        if not key:
            key = "%s%s" % (remove_accents(ref.authors[0][0]),ref.year)
        
        key = self.pick_key(key)
        self.refs[key] = ref
        return key
    
    def pick_key(self, k):
        key = k
        sup = ord("a")
        while key in self.refs:
            key = k + chr(sup)
            sup += 1
        return key
    
    def get(self, key):
        return self.refs[key]
    
    def find(self, key, value):
        for ref in self.refs.values():
            if key in ref.links and ref.links[key] == value:
                return ref
    
    def get_references(self):
        return self.refs
    
    def search(self, args):
        pass
    
    def save(self):
        if not self.refs:
            return
        
        encoder = json.JSONEncoder()
        f = open(self.path, "w")
        f.write("{\n")
        isfirst = True
        for key in sorted(self.refs.keys()):
            ref = self.refs[key]
            if isfirst:
                isfirst = False
            else:
                f.write(",\n")
            
            f.write('"%s": %s' % (key,ref.encode(encoder)) )
            
        f.write("\n}\n")
        f.close()
    
    def save_ref(self, key, folder):
        if not self.refs:
            return
        
        if key not in self.refs:
            print("No such ref: "+key)
            return
        
        ref = self.refs[key]
        
        encoder = json.JSONEncoder()
        f = open("%s/%s.json" % (folder, key), "w")
        f.write(ref.encode(encoder))
        f.close()


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if unicodedata.category(c)[0] == 'L' and not unicodedata.combining(c) ])


