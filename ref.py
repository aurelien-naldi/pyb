#!/usr/bin/env python3

from __init__ import *
import os
import sys
import plugins

def main(args):
    """Simple CLI to load a ref from the proper source depending on the argument

Usage
=====
ref.py <command> <arguments>
"""
    
    collection = RefCollection()
    
    if len(args) < 2:
        help(short=True)
        return
    
    command = args[1]
    if command not in plugins.commands:
        if command in plugins.aliases:
            command = plugins.aliases[command]
    
    if command not in plugins.commands:
        print("Unknown command")
        help(short=True)
        return
    
    plugins.commands[command](collection, args[2:])


def get_short_doc(n):
    # TODO: cut long doc and show some kind of ellipsis
    doc = n.__doc__.strip()
    cut = doc.find("\n\n")
    if cut > 0:
        return doc[:cut]+"  [...]"
    return doc


@plugins.command_aliases("h,?")
def help(collection=None, args=None, short=False):
    "Print the main help message or the long help for a specific command."
    if args:
        command = args[0]
        if command in plugins.commands:
            print('Showing full help for "%s"' % command)
            print(plugins.commands[command].__doc__)
            return
            
        for n in plugins.providers:
            if n.name == command:
                print('Showing help for provider "%s"' % command)
                print(n.__doc__)
                return
        
        print("Unknown keyword: %s" % command)
        return
    
    print (main.__doc__)
    print()
    if short:
        print("Commands:")
        for n in plugins.commands.keys():
            print(n, end=" ")
        print("\n")
        
        print("Metadata providers:")
        for n in plugins.providers:
            print(n.name, end=" ")
        print("\n")
        
        return
    
    # Show full overview
    print("Commands")
    print("========")
    print()
    for n in plugins.commands.keys():
        doc = get_short_doc(plugins.commands[n])
        aliases = plugins.get_command_aliases(n)
        print("%s%s:\n%s\n" % (n, aliases, doc) )
    
    print()
    print("Providers")
    print("=========")
    print()
    for n in plugins.providers:
        doc = get_short_doc(n)
        print("%s:\n%s\n" % ( n.name, doc))
    print()

@plugins.command_aliases("lk,pull")
def lookup(collection, args):
    """Lookup metadata for a reference: call all providers on the specified names.
It will propose to add the matching references to the "database".

Note: when a match is found by several metadata providers, it saves alternative fields on the side."""

    for key in args:
        ref = do_lookup(key)
        if not ref:
            print( "NO MATCH for "+key )
            continue
        print( "Found "+key )
        print(ref)
        print()
        askAdd = input("Add this ref? [y/N] ")
        if askAdd.strip().lower() == "y":
            key = collection.add_reference(ref)
            collection.save()
            print("Reference added: "+key)
        else:
            print("NOT added")

def do_lookup(key):
    main_ref = None
    for p in plugins.providers:
        try:
            ref = p.load_ref(key)
        except:
            print("error in "+p.name)
            ref = None
        
        if not ref:
            continue
        
        ref = Ref(ref)
        if main_ref:
            main_ref.add_alternative(ref)
        else:
            main_ref = ref
    
    return main_ref

@plugins.command_aliases("import")
def import_file(collection, args):
    """Import an existing file in the collection"""

    for path in args:
        if not os.path.exists(path):
            print("no such file: "+path)
            continue
        
        extension = path.split(".")[-1]
        if extension not in plugins.importers:
            print("no importer for "+extension)
            return
        
        p = plugins.importers[extension]
        try:
            refs = p.import_file(path)
        except:
            print("error in "+p.name)
            continue
        
        l = len(refs)
        if l < 1:
            print("No ref found")
            return
        
        refs = [ Ref(ref) for ref in refs ]
        for r in refs:
            print(r)
        
        askAdd = raw_input("Add these %s refs? [y/N] " % len(refs))
        if askAdd.strip().lower() == "y":
            keys = []
            for ref in refs:
                keys.append( collection.add_reference(ref) )
            collection.save()
            print("References added: ", keys)
        else:
            print("NOT added")


@plugins.command_aliases("ls,l")
def list(collection, args):
    "List all stored references"
    tag = None
    if len(args) == 1: tag = args[0]
    refs = collection.get_references(tag)
    for key in sorted(refs.keys()):
        ref = refs[key]
        print("[%s]" % key)
        print( ref.short() )
        print()

@plugins.add_command
def search(collection, args):
    """Search in the stored references
NOT YET IMPLEMENTED"""
    
    result = collection.search(args)
    if result:
        print(result)

@plugins.add_command
def show(collection, args):
    """show specific refs"""
    for key in args:
        ref = collection.get(key)
        print( ref)

@plugins.add_command
def save(collection, args):
    """save specific refs.
Usage: save <ref1> <ref2> <dest_folder>"""
    if len(args) < 2:
        print( "mising arguments")
        return
    
    destfolder = args[-1]
    if not os.path.isdir(destfolder):
        print("The destination must be a folder")
        return
    
    for key in args[:-1]:
        collection.save_ref(key, destfolder)

if __name__ == "__main__":
    main( sys.argv )

