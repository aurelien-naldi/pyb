import re

DOI_PATTERN = "(^|\s|doi:|http[s]?://dx[.]doi[.]org/)(10[.][0-9]{2}[0-9]+/[^\s'\"&<>]*)($|\s)"

def get_doi(string):
    """try to extract a DOI from a string.
    it will match a pure DOI, the "doi:" prefix or a doi resolution URL.
    
    returns the pure DOI or None if no match is found.
    """
    m = re.search(DOI_PATTERN, string)
    if m:
        return m.groups()[1]

def ref_load(plugins):
    # empty function to avoid the "no entry point" message
    pass

