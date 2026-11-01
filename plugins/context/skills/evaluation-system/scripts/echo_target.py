#!/usr/bin/env python3
"""Trivial target adapter: read one case's input as JSON on stdin and write it back as JSON on stdout."""
import json
import sys

json.dump(json.load(sys.stdin), sys.stdout)
