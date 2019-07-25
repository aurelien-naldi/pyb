#!/usr/bin/env python3

import sys
import re

DOI_PATTERN = re.compile("(^|\s|doi:|http[s]?://(dx[.])?doi[.]org/)(10[.][0-9]{2}[0-9]+/[^\s'\"&<>]*)($|\s)")

def get_doi(string):
    """try to extract a DOI from a string.
    it will match a pure DOI, the "doi:" prefix or a doi resolution URL.
    
    returns the pure DOI or None if no match is found.
    """
    
    m = DOI_PATTERN.match(string)
    if m:
        return m.groups()[2]

def ref_load(plugins):
    # empty function to avoid the "no entry point" message
    pass



def main(args):
    "Simple CLI to test if the argument contains a valid DOI"
    
    if len(args) != 2:
        print( "Usage: %s <DOI>" % args[0] )
        return
    
    print( get_doi(args[1]) )


if __name__ == "__main__":
    main( sys.argv )

