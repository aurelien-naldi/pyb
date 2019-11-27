#!/usr/bin/env python3

from __future__ import print_function
from doi import get_doi
from urllib.request import urlopen,Request
import sys
import re

try:
    from Bio import Entrez
    Entrez.email = 'contact@colomoto.org'
    _HAS_DEPS = True
    
    def ref_load(plugins):
        plugins.add_provider(PubmedProvider())

except:
    print( "Missing deps for the pubmed provider" )
    _HAS_DEPS = False

PM_PATTERN = "^((pmid|pubmed):)?(\d*)$"
PM_PATTERN_LONG = "http[s]?://www[.]ncbi[.]nlm[.]nih[.]gov/pubmed/(\d*)([?].*)$"




def test_raw():
    import bs4
    base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    fetch = "efetch.fcgi?db=pubmed&id=%s&rettype=xml&retmode=text"
    url = base+fetch % "4655"

    xml = urlopen(url).read()
    soup = bs4.BeautifulSoup(xml)

    article = soup.find("article")
    print(soup)

class PubmedProvider:
    "Find metadata on Pubmed"
    def __init__(self):
        self.name = "pubmed"
    
    def load_ref(self, key):
        # Look for a corresponding entry in pubmed
        
        pmid = self.get_pmid(key)
        
        if pmid:
            return self.load_pubmed(pmid)
    
    def get_pmid(self, string):
        m = re.search(PM_PATTERN, string)
        if m:
            return m.groups()[2]
        
        m = re.search(PM_PATTERN_LONG, string)
        if m:
            return m.groups()[0]
        
        doi = get_doi(string)
        if doi:
            return self.find_pmid_for_doi(doi)

    def find_pmid_for_doi(self, doi):
        "Search a pubmed entry for a given doi, return None if not found (or multiple matches)"
        
        handle = Entrez.esearch(db='pubmed', term=doi+"[doi]", retmax=3)
        record = Entrez.read(handle)
        handle.close()
        
        results = record["IdList"]
        if len(results) != 1:
            return None
        
        return results[0]
    
    
    def load_pubmed(self, pmid):
        """Load a reference from pubmed.
        This will retrieve the metadata from pubmed, and create a Ref object based on it.
        """
        handle = Entrez.efetch(db='pubmed', id=pmid, retmode='text', rettype='xml')
        record = Entrez.read(handle)['PubmedArticle'][0]['MedlineCitation']['Article']
        
        title = record["ArticleTitle"]
        authors = []
        for a in record["AuthorList"]:
            if "LastName" in a:
                authors.append( (a["LastName"], a["ForeName"]) )
            else:
                authors.append((a["CollectiveName"],""))
        
        journal = record["Journal"]
        journal_name  = journal["ISOAbbreviation"]
        journal_issue = journal["JournalIssue"]
        vol, issue = None,None
        if "Volume" in journal_issue:
            vol = journal_issue["Volume"]
        if "Issue" in journal_issue:
            issue = journal_issue["Issue"]
        year = journal_issue["PubDate"]["Year"]
        
        pages = record["Pagination"]["MedlinePgn"]
        
        ref = {
            "title": title,
            "authors": authors,
            "journal": journal_name,
            "year": year,
            "volume": vol,
            "issue": issue,
            "pages": pages
        }
        
        ref_links = {"pmid":pmid}
        ref["links"] = ref_links
        
        links = record["ELocationID"]
        for l in links:
            ref_links[l.attributes["EIdType"]] = l.title()
        
        handle.close()
        return ref


def main(args):
    "Simple CLI to load a ref from the proper source depending on the argument"
    if len(args) != 2:
        print( "Usage: %s <ID>" % args[0] )
        print("The ID can be a pubmedID (numeric value) or a doi")
        return
    
    provider = PubmedProvider()
    ref = provider.load_ref(args[1])
    print( ref )

if __name__ == "__main__":
    main( sys.argv )
    #test_raw()
