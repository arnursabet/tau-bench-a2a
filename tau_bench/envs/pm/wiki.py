
import os

_current_dir = os.path.dirname(__file__)
_wiki_path = os.path.join(_current_dir, "wiki.md")

with open(_wiki_path, "r") as f:
    WIKI = f.read()
