from doctest import master
from tkinter import filedialog

def folder_asking(ask_parent):
    folderpath = filedialog.askdirectory(parent=ask_parent)
    return folderpath