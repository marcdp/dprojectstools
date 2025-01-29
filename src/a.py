#!/usr/bin/env python3

from dprojectstools.editor import Editor

text = ""
with open("../.gitignore", "r") as file:
#with open("../LICENSE", "r") as file:
    text = file.read()

editor = Editor()
editor.editFile("d:\\Reps\\dprojectstools\\README2.md")
#editor.editText(text)
