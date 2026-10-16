import os
from pathlib import Path
import pygetwindow as gw


def search(root=".", pattern="*"):
    """Find filer i en mappe og alle dens undermapper. Bruges til at finde ud af, hvor en fil ligger.

    Args:
        root: Mappen der søges fra, fx "C:/Users/navn/Documents".
        pattern: Filmønster, fx "*.xlsx" for Excel-filer eller "*.pdf" for PDF-filer.
    """
    return [str(p) for p in Path(root).rglob(pattern)]


def open(path):
    """Åbn en fil på computeren i det program, der hører til filtypen.

    Args:
        path: Den fulde sti til filen, fx fundet med search.
    """
    os.startfile(path)


def close(path):
    """Luk vinduet med en fil, der er åben på computeren.

    Args:
        path: Stien eller navnet på den åbne fil.
    """
    for w in gw.getWindowsWithTitle(Path(path).name):
        w.close()

