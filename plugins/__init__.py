#!/usr/bin/env python

from __future__ import print_function
import imp
import sys
import os

def load_plugins():
    basedir = os.path.dirname(__file__)
    expected_entry = 'ref_load'
    module = sys.modules[__name__]
    
    for name in os.listdir(basedir):
        if name.endswith(".py") and not name.startswith("_"):
            try:
                filepath = os.path.join(basedir, name)
                mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
                py_mod = imp.load_source(mod_name, filepath)

                if hasattr(py_mod, expected_entry):
                    getattr(py_mod, expected_entry)(module)
            except:
                print("Error loading "+mod_name)

def add_provider(provider):
    providers.append(provider)

def command_aliases(cmd_aliases):
    def decorator(f):
        return add_command(f, cmd_aliases)
    return decorator

def add_command(function, cmd_aliases=None):
    name = function.func_name
    if name in commands:
        print("Command %s already exists" % name)
        return function
    commands[name] = function
    
    if cmd_aliases:
        cmd_aliases = [a.strip() for a in cmd_aliases.split(",")]
        command2aliases[name] = cmd_aliases
        for alias in cmd_aliases:
            if alias in aliases:
                print("Existing alias: %s" % alias)
                continue
            aliases[alias] = name
    
    return function

def get_command_aliases(name):
    if name in command2aliases:
        return " [%s]" % ",".join(command2aliases[name])
    return ""

# list of providers, to be loaded from plugins
providers = []
commands = {}
aliases = {}
command2aliases = {}

load_plugins()

