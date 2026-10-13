import os
from pathlib import Path
import pygetwindow as gw





def search(root=".", pattern="*"):
    return [str(p) for p in Path(root).rglob(pattern)]


def open(path):
    os.startfile(path)


def close(path):
    for w in gw.getWindowsWithTitle(Path(path).name):
        w.close()


#print(search_files())
open('tester')
close('tester')