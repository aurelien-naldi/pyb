This small project provides a minimalistic representation of references and a few tools to manipulate them.


List of references
==================




Plugins
=======

all modules in the plugins folder will be loaded (from the plugins/__init__.py file),
if they define a function named "ref_load", it will be called with the plugins module as argument.

The current plugins use this function to add a provider to the plugins.
A provider is a class with a "load_ref" method, which takes a key as input and returns a dict representing a reference (or None).
The plugins are otherwise valid python files on their own, they do not require the rest of the code to work:
they can be called independently to lookup a reference.

Current plugins:
* pubmed (requires BioPython): retrieve metadata from pubmed. It will recognize a pubmed ID or URL. It can also lookup based on a DOI
* bibtex (requires bibtexparser): retrieve a piece of bibtex from the DOI system and load it.
* meta (requires BeautifulSoup4): extracts metadata from the <meta name="citation_*"> tags of a html document


