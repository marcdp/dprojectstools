import re
from ..console import Sequences, Keys, readKey
from ..crypto import aes_decrypt, aes_encrypt
from ..clipboard import copy
import sys
import os
import getpass
import json
import json5
import yaml
from datetime import datetime, timezone
from dataclasses import dataclass, field
from .hightlight_none import  hightlight_none
from .hightlight_env import  hightlight_env
from .hightlight_md import  hightlight_md
from .hightlight_json import  hightlight_json


# constants
TAB_SPACES = 4

# class
@dataclass(slots=True)
class HistoryEntry:
    cursor_x: int = 0
    cursor_y: int = 0
    inserted: str = ""
    deleted: str = ""


# class
class XEditor:
  
    # ctor
    def __init__(self) -> None:
        # init
        self._stdout = sys.stdout
        self._filename = None
        self._cols , self._rows = os.get_terminal_size()
        self._insert = True
        self._dirty = False
        self._encoding = "utf-8"
        self._lines = []
        self._readonly = False
        self._stop = False
        self._newline = os.linesep
        self._password = None
        self._format = ""
        self._use_buffers = True
        self._result = None
        self._keyword = None
        self._use_quit_escape = False
        self._title = None
        self._line_hightlight = True
        self._undo_stack = []
        self._redo_stack = []
        # cursor
        self._cursor_x = 0
        self._cursor_y = 0
        self._cursor_y_prev = 0
        # offset
        self._offset_x = 0
        self._offset_y = 0
        # select
        self._select_x = None
        self._select_y = None

    # methods
    def editFile(self, filename: str, password: str = None, dump: bool = False):
        # password
        if password != None:
            self._password = password
        elif filename != None and filename.endswith(".aes"):
            self._password = getpass.getpass(f"Enter password for '{filename}': ")
        else:
            self._password = None            
        # format
        if filename.endswith(".json.aes") or filename.endswith(".json"):
            self._format = "json"
        elif filename.endswith(".jsonc.aes") or filename.endswith(".jsonc"):
            self._format = "jsonc"
        elif filename.endswith(".env.aes") or filename.endswith(".env"):
            self._format = "env"
        elif filename.endswith(".xml.aes") or filename.endswith(".xml"):
            self._format = "xml"
        elif filename.endswith(".md.aes") or filename.endswith(".md"):
            self._format = "md"
        elif filename.endswith(".yaml.aes") or filename.endswith(".yaml") or filename.endswith(".yml.aes") or filename.endswith(".yml"):
            self._format = "yaml"
        else:
            self._format = None
        # load
        try:
            self.load(filename)
        except ValueError as e:
            print("error: " + str(e))
            return False
        # dump
        if dump:
            text = self._newline.join(self._lines)
            print(text)
            return True
        # loop
        try:
            # buffer alternate
            if self._use_buffers:
                self._stdout.write(Sequences.BUFFER_ALTERNATE)
            # loop
            self._loop()
        finally:
            # buffer main
            if self._use_buffers:
                self._stdout.write(Sequences.BUFFER_MAIN)
            pass
        # return
        return True

    def editText(self, text:str, format:str = "", newline:str = None, readonly: bool = False, use_quit_escape: bool = False, title: str = None, use_buffers: bool = True):
        # load
        if newline is not None:
            self._newline = newline
        else:
            self._newline = self.autodetect_newline(text)
        self._lines = [line for line in text.splitlines()]
        if text.endswith("\n"):
            self._lines.append("")
        self._filename = None
        self._format = format
        self._readonly = readonly
        self._title = title
        self._use_buffers = use_buffers
        self._use_quit_escape = use_quit_escape
        # loop
        try:
            # buffer alternate
            if self._use_buffers:
                self._stdout.write(Sequences.BUFFER_ALTERNATE)
            # loop
            self._loop()
        finally:
            # buffer main
            if self._use_buffers:
                self._stdout.write(Sequences.BUFFER_MAIN)
            pass
        # return
        return self._result        
        

    # keys
    def down(self, select = False):
        # select 
        printLine = self._setSelect(select)        
        # if select then print line
        if printLine:
            cursor_x_prev = self._cursor_x
            self._cursor_x = len(self._lines[self._cursor_y]) 
            self._setSelect(select)        
            self._printLine(self._cursor_y)
            self._cursor_x = cursor_x_prev
        # left
        if self._cursor_y < len(self._lines) - 1:
            self._setCursor(self._cursor_x, self._cursor_y + 1)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def up(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # if select then print line
        if printLine:
            cursor_x_prev = self._cursor_x
            self._cursor_x = 0 
            self._setSelect(select)        
            self._printLine(self._cursor_y)
            self._cursor_x = cursor_x_prev
        # move
        if self._cursor_y > 0:
            self._setCursor(self._cursor_x, self._cursor_y - 1)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def left(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # left
        line = self._lines[self._cursor_y]
        if self._cursor_x > 0:
            self._setCursor( self._cursor_x - 1, self._cursor_y)
        elif self._cursor_y > 0:
            line = self._lines[self._cursor_y - 1]
            self._setCursor( len(line), self._cursor_y - 1)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def leftWord(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # move left
        cursor_y = self._cursor_y
        cursor_x = self._cursor_x
        line = self._lines[cursor_y]
        if cursor_x == 0 and cursor_y > 0:
            cursor_y -= 1
            cursor_x = len(self._lines[cursor_y])
            line = self._lines[cursor_y]
        alnumFound = False
        for char in ''.join(reversed(line[:cursor_x])):
            if alnumFound and not char.isalnum():
                break
            if char.isalnum():
                alnumFound = True
            cursor_x -= 1
        self._setCursor(cursor_x, cursor_y)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)
    
    def right(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # move right
        line = self._lines[self._cursor_y]
        if self._cursor_x < len(line):
            self._setCursor( self._cursor_x + 1, self._cursor_y)
        elif self._cursor_y < len(self._lines) - 1:
            self._setCursor( 0, self._cursor_y + 1)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def rightWord(self, select = False):
        # select
        printLine = self._setSelect(select)        
        #move right
        cursor_y = self._cursor_y
        cursor_x = self._cursor_x
        line = self._lines[cursor_y]
        if cursor_x >= len(line) and cursor_y < len(self._lines) - 1:
            cursor_y += 1
            cursor_x = 0
            line = self._lines[cursor_y]
        alnumFound = False
        for char in line[cursor_x:]:
            if alnumFound and not char.isalnum():
                break
            if char.isalnum():
                alnumFound = True
            cursor_x += 1
        self._setCursor( cursor_x, cursor_y )
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)
    
    def home(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # move
        self._setCursor(0, self._cursor_y)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def end(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # nmove to end
        line = self._lines[self._cursor_y]
        self._setCursor(len(line), self._cursor_y)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def pageUp(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # move
        self._setCursor(self._cursor_x, self._cursor_y - self._rows - 2)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def pageDown(self, select = False):
        # select
        printLine = self._setSelect(select)        
        # move
        self._setCursor(self._cursor_x, self._cursor_y + self._rows - 2)
        # if select then print line
        if printLine:
            self._printLine(self._cursor_y)

    def scrollUp(self):
        # scroll up
        self._setOffset(self._offset_x, self._offset_y - 1)
        self._printCursor()
        
    def scrollDown(self):
        # scroll down
        self._setOffset(self._offset_x, self._offset_y + 1)
        self._printCursor()

    def scrollTop(self):
        # scroll top
        self._setCursor(self._cursor_x, 0);
        self._printCursor()

    def scrollBottom(self):
        # scroll bottom
        self._setCursor(self._cursor_x, len(self._lines) - 1);
        self._printCursor()

    def keypress(self, key):
        # keypress
        if len(key) > 1:
            print("UNHANDLED SEQUENCE: ", key.replace("\x1b", "ESC"))
            return
        elif len(key)==1 and ord(key[0]) < 32:
            print("UNHANDLED KEY: ", ord(key[0]))
            return
        
        if self._readonly:
            pass
        elif self._select_x != None:
            self._dirty = True
            self.setSelectedText(key)
        elif self._insert:
            self._dirty = True
            line = self._lines[self._cursor_y]
            line = line[:self._cursor_x] + key + line[self._cursor_x:]
            self._lines[self._cursor_y] = line            
            self._setCursor(self._cursor_x + 1, self._cursor_y)
            self._printHeader(flush = False)            
            self._printLine(self._cursor_y, flush = False)
            self._printCursor()

            # add to undo stack
            self._undo_stack.append(HistoryEntry(
                cursor_x = self._cursor_x - 1,
                cursor_y = self._cursor_y,
                inserted = key,
            ))
            self._redo_stack.clear()

        else:
            self._dirty = True
            line = self._lines[self._cursor_y]
            deleted = line[self._cursor_x:self._cursor_x + 1]
            line = line[:self._cursor_x] + key + line[self._cursor_x + 1:]
            self._lines[self._cursor_y] = line            
            self._setCursor(self._cursor_x + 1, self._cursor_y)
            self._printHeader(flush = False)
            self._printLine(self._cursor_y)        

            # add to undo stack
            self._undo_stack.append(HistoryEntry(
                cursor_x = self._cursor_x - 1,
                cursor_y = self._cursor_y,
                deleted = deleted,
                inserted = key,
            ))
            self._redo_stack.clear()
    
    def enter(self):
        # enter
        if self._readonly:
            pass
        elif self._select_x != None:
            self._dirty = True
            self.setSelectedText("\n")
        else:
            self._dirty = True
            line = self._lines[self._cursor_y]
            line_before = line[:self._cursor_x]
            line_after = line[self._cursor_x:]
            self._lines[self._cursor_y] = line_before
            self._lines.insert(self._cursor_y + 1, line_after)
            self._setCursor(0, self._cursor_y + 1)
            self._printHeader(flush = False)
            self._printLines(flush = False)
            self._printCursor()
        
    def tab(self):
        # tab
        if self._readonly:
            pass
        elif self._select_x == None:
            # nothing selected, insert spaces
            spaces = " " * (TAB_SPACES - (self._cursor_x % TAB_SPACES))
            self.insertText(spaces)
        elif self._select_y == self._cursor_y and abs(self._select_x - self._cursor_x) != len(self._lines[self._cursor_y]):
            # text selected in the same line
            self.setSelectedText("")
            spaces = " " * (TAB_SPACES - (self._cursor_x % TAB_SPACES))
            self.insertText(spaces)
        else:
            # multime lines selected (indent as a block)
            x1 = self._cursor_x
            y1 = self._cursor_y
            x2 = self._select_x
            y2 = self._select_y
            if y1 > y2:
                x2, x1 = x1, x2
                y2, y1 = y1, y2
            selected_line_count = y2 - y1 + 1
            if x2 > 0 or selected_line_count == 1:
                y2 += 1
            for y in range(y1,y2):
                self._lines[y] = (" " * TAB_SPACES) + self._lines[y]
            # if one line was selected, then reselect entire line
            if selected_line_count == 1:
                if x1 < x2:
                    self._setCursor(0, y1)
                    self._select_x = len(self._lines[y1])
                    self._select_y = y1                
                else:
                    self._setCursor(len(self._lines[y1]), y1)
                    self._select_x = 0
                    self._select_y = y1                
            # print 
            self._printHeader(flush = False)
            self._printLines(flush = False)
            self._printCursor()

    def untab(self):
        # untab
        spaces = " " * TAB_SPACES
        if self._readonly:
            pass
        elif self._select_x == None or self._select_y == self._cursor_y:
            # nothing selected
            line = self._lines[self._cursor_y]
            if line.startswith(spaces):
                line = line[len(spaces):]
                self._lines[self._cursor_y] = line
                self._setCursor(self._cursor_x - TAB_SPACES, self._cursor_y)
                if self._select_x != None:
                    self._select_x -= TAB_SPACES
                self._printHeader(flush = False)
                self._printLines(flush = False)
                self._printCursor()
        else:
            # multime lines selected (unindent as a block)
            x1 = self._cursor_x
            y1 = self._cursor_y
            x2 = self._select_x
            y2 = self._select_y
            if y1 > y2:
                x2, x1 = x1, x2
                y2, y1 = y1, y2
            selected_line_count = y2 - y1 + 1
            if x2 > 0 or selected_line_count == 1:
                y2 += 1
            # unindent
            for y in range(y1,y2):
                line = self._lines[y]
                if line.startswith(spaces):
                    line = line[len(spaces):]
                    self._lines[y] = line
            # print 
            self._printHeader(flush = False)
            self._printLines(flush = False)
            self._printCursor()

    def backspace(self):
        # backspace
        line = self._lines[self._cursor_y]
        if self._readonly:
            pass
        elif self._select_x != None:
            self.setSelectedText("")
        elif self._cursor_x == 0:
            if self._cursor_y > 0:
                self._dirty = True
                line_prev = self._lines[self._cursor_y - 1]
                line = line_prev + line
                self._lines[self._cursor_y - 1] = line
                self._lines.pop(self._cursor_y)
                self._setCursor(len(line_prev), self._cursor_y - 1)
                self._printHeader(flush = False)
                self._printLines(flush = False)
                self._printCursor()
        else:
            self._dirty = True
            line = line[:self._cursor_x - 1] + line[self._cursor_x:]
            self._lines[self._cursor_y] = line            
            self._setCursor(self._cursor_x - 1, self._cursor_y)
            self._printHeader(flush = False)
            self._printLine(self._cursor_y)

    def delete(self):
        # delete
        line = self._lines[self._cursor_y]
        if self._readonly:
            pass
        elif self._select_x != None:
            self.setSelectedText("")
        elif self._cursor_x == len(line):
            if self._cursor_y < len(self._lines) - 1:
                self._dirty = True
                line += self._lines[self._cursor_y + 1]
                self._lines[self._cursor_y] = line            
                self._lines.pop(self._cursor_y + 1)
                self._printHeader(flush = False)
                self._printLines(flush = False)
                self._printCursor()
        else:
            self._dirty = True
            line = line[:self._cursor_x] + line[self._cursor_x + 1:]
            self._lines[self._cursor_y] = line            
            self._printHeader(flush = False)
            self._printLine(self._cursor_y)

    def insert(self):
        # insert
        self._insert = not self._insert
        self._printHeader(flush = False)
        self._printCursor()

    def escape(self):
        # escape
        if self._use_quit_escape:
            self.quit()

    def snapshot(self):
        # snapshot changes between the last iteration
        pass

    def undo(self):
        # undo
        if self._undo_stack:
            # pop from undo stack
            entry = self._undo_stack.pop()
            # apply edit
            line = self._lines[entry.cursor_y]
            if entry.deleted:
                line = line[:entry.cursor_x] + entry.deleted + line[entry.cursor_x + len(entry.deleted):]
                self._cursor_x = entry.cursor_x
                self._cursor_y = entry.cursor_y
            elif entry.inserted:
                line = line[:entry.cursor_x] + line[entry.cursor_x + len(entry.inserted):]
                self._cursor_x = entry.cursor_x
                self._cursor_y = entry.cursor_y
            self._lines[entry.cursor_y] = line
            self._printLine(entry.cursor_y)
            # push to redo_stack
            self._redo_stack.append(entry)

    def redo(self):
        # redo
        if self._redo_stack:
            # pop from redo stack
            entry = self._redo_stack.pop()
            # apply reverse edit
            pass
            # push to undo_stack
            self._undo_stack.append(entry)

    def goto(self):
        number = self._question("Go to line:")
        if number != None:
            try:
                line = int(number)
                self._setCursor(self._cursor_x, line - 1)
            except ValueError:
                pass

    def find(self, previous = False):
        # find
        keyword = self._question("Find:")
        if keyword:
            self._keyword = keyword
            if previous:
                self.findPrevious()
            else:
                self.findNext()

    def findNext(self, from_start = False):
        # find next occurrence of keyword
        if from_start:
            y = 0
        else:
            y = self._cursor_y
        found = False
        while y < len(self._lines):
            line = self._lines[y]
            if y == self._cursor_y and not from_start:
                x = line.find(self._keyword, self._cursor_x + 1)
            else:
                x = line.find(self._keyword)
            if x >= 0:
                self._setSelect(False)
                self._printLine(y)
                self._setCursor(x, y)
                self._select_y = y
                self._select_x = x + len(self._keyword)
                self._printLine(y)
                found = True
                break
            y += 1
        if not found:
            # if not found, then check if found before cursor
            for line in self._lines:
                x = line.find(self._keyword)
                if x >= 0:
                    self.findNext(True)
                    break

    def findPrevious(self, from_bottom = False):
        # find previous occurrence of keyword
        if from_bottom:
            y = len(self._lines) - 1
        else:
            y = self._cursor_y
        found = False
        while y >= 0:
            line = self._lines[y]
            if y == self._cursor_y and not from_bottom:
                x = line.rfind(self._keyword, 0, self._cursor_x)
            else:
                x = line.rfind(self._keyword)
            if x >= 0:
                self._setSelect(False)
                self._printLine(y)
                self._setCursor(x, y)
                self._select_y = y
                self._select_x = x + len(self._keyword)
                self._printLine(y)
                found = True
                break
            y -= 1
        if not found:
            # if not found, then check if found before cursor
            for line in self._lines:
                x = line.rfind(self._keyword)
                if x >= 0:
                    self.findPrevious(True)
                    break

    def insertText(self, text, x = None, y = None):
        # print
        if x == None:
            x = self._cursor_x
        if y == None:
            y = self._cursor_y
        # action
        for char in text:
            if char == '\n':
                y += 1
                x = 0
            else:
                line = self._lines[y]
                line = line[:x] + char + line[x:]
                x += 1
                self._lines[y] = line
        # print
        self._setCursor(x, y)
        self._printHeader(flush = False)
        self._printLines(flush = False)
        self._printCursor()

    def getSelectedText(self):
        # get selected text
        if self._select_x == None:
            return None
        # coords
        x1 = self._select_x - self._offset_x
        y1 = self._select_y
        x2 = self._cursor_x - self._offset_x
        y2 = self._cursor_y
        # reorder dots
        if y1 < y2:
            pass
        elif y1 == y2:
            if x1 > x2:
                x1,x2 = x2,x1    
        elif y1 > y2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1
        # return
        y = y1
        result = []
        while y < len(self._lines):
            line = self._lines[y]
            if y == y1:
                if y==y2:
                    result.append(line[x1:x2])
                else:
                    result.append(line[x1:])
            elif y1 < y < y2:
                result.append(self._lines[y])
            elif y == y2:
                result.append(line[:x2])
                break
            y += 1
        # join and return
        return self._newline.join(result)

    def setSelectedText(self, text):
        # select all
        x1 = self._select_x - self._offset_x
        y1 = self._select_y
        x2 = self._cursor_x - self._offset_x
        y2 = self._cursor_y
        # reorder dots
        if y1 < y2:
            pass
        elif y1 == y2:
            if x1 > x2:
                x1,x2 = x2,x1    
        elif y1 > y2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1
        # remove
        y = y2
        remainder = ""
        while True:
            line = self._lines[y]
            if y == y1:
                if y==y2:
                    self._lines[y] = line[0:x1] + line[x2:]
                else:
                    self._lines[y] = line[0:x1] + remainder
                break
            elif y1 < y < y2:
                self._lines.pop(y)
                pass
            elif y == y2:
                remainder = line[x2:]
                self._lines.pop(y)
                pass
            y -= 1
        # insert text
        self._setSelect(False)
        self._setCursor(x1, y1)
        self.insertText(text)
        
    def selectAll(self):
        # select all
        self._select_x = 0
        self._select_y = 0
        self._setCursor(len(self._lines[-1]), len(self._lines) -1 )
        self._printHeader(flush = False)
        self._printLines(flush = False)
        self._printCursor()

    def help(self):
        # help
        help = """ 
  XEditor - a simple terminal text editor

  Cursor movement
    Arrows              Move cursor
    Home / End          Move to beginning / end of line
    PageUp / PageDown   Move one page up / down
    Ctrl+Arrows         Move cursor by word
    Ctrl+G              Go to line
  Indentation
    Tab                 Indent
    Untab               Unindent
    Ctrl+Tab            Indent as a block
    Ctrl+Untab          Unindent as a block
  Selection
    Ctrl+A              Select all
  Editing
    Ctrl+C              Copy
    Ctrl+X              Cut
    Ctrl+V              Paste
    Ctrl+Z              Undo
    Ctrl+Y              Redo
  Search
    Ctrl+F              Find
    F3                  Find next
    Shift+F3            Find previous
  File
    Ctrl+S              Save
    Ctrl+Q              Quit
        """
        self._info(help)

    def cutAndCopy(self):
        # cut and copy
        if self._select_x != None:
            self.copy()
            self.setSelectedText("")

    def copy(self):
        # copy
        text = self.getSelectedText()
        copy(text)

    def load(self, filename):
        # load
        self._lines = [""]
        self._newline = os.linesep
        self._readonly = False
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                text = file.read()
                # decrypt
                if self._password != None:
                    text = aes_decrypt(text, self._password)
                # split in lines
                self._newline = self.autodetect_newline(text)
                self._lines = [line.rstrip(self._newline) for line in text.splitlines()]
            self._readonly = not os.access(filename, os.W_OK)
        self._filename = filename
        self._dirty = False
        self._offset_x = 0
        self._offset_y = 0
        self._cursor_x = 0
        self._cursor_y = 0
        
    def save(self):
        # validate format
        if not self._validateFormat():
            
            return False
        # encrypt if required
        text = self._newline.join(self._lines)
        if self._password != None:
            text = aes_encrypt(text, self._password)
        # save
        if self._filename == None:
            self._result = self._newline.join(self._lines)
        else:
            with open(self._filename,"w", encoding="utf-8") as file:
                file.write(text)
        # print
        self._dirty = False
        self._printAll()
        return True

    def quit(self):
        # exit
        if self._dirty:
            result = self._questionYesNo("Save changes? [Y/n]")
            if result == "y" or result == "Y":
                if not self.save():
                    return False                
            elif result == "n" or result == "N":
                self._result = None
            elif result == None:
                return False
        self._printAll()
        self._stop = True        
        return True

    # utils
    def _setSelect(self, select: bool):
        if select:
            if self._select_x == None:
                self._select_x = self._cursor_x
                self._select_y = self._cursor_y
        else:
            if self._select_x != None:
                self._select_x = None
                self._select_y = None
                self._printLines()
            self._select_x = None
            self._select_y = None
        return self._select_x != None
        
    def _setOffset(self, x, y):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        changed = (self._offset_x != x or self._offset_y != y)
        self._offset_x = x
        self._offset_y = y
        if changed:
            self._printLines()
    
    def _setCursor(self, x, y):        
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if y > len(self._lines) - 1:
            y = len(self._lines) - 1
        self._cursor_x = x
        self._cursor_y = y

        if self._cursor_x > len(self._lines[y]):
            self._cursor_x = len(self._lines[y])

        if self._cursor_x <= self._offset_x:
            self._setOffset(self._cursor_x, self._offset_y)
        if self._cursor_x >= self._offset_x + self._cols:
            self._setOffset( self._cursor_x - self._cols + 1, self._offset_y)

        if self._cursor_y <= self._offset_y:
            self._setOffset(self._offset_x, self._cursor_y)
        if self._cursor_y >= self._offset_y + self._rows - 1:
            self._setOffset(self._offset_x, self._cursor_y - self._rows + 1 + 1)

        self._printHeader(flush = False)
        self._printCursor()

        if self._line_hightlight and self._cursor_y_prev != self._cursor_y:
            self._printLine(self._cursor_y_prev)
            self._printLine(self._cursor_y)
        self._cursor_y_prev = self._cursor_y
    
    def autodetect_newline(self, text: str) -> str:
        result = os.linesep
        if "\r\n" in text:
            result = "\r\n"
        elif "\n" in text:
            result = "\n"
        return result
    
    def _clear(self):
        self._stdout.write(Sequences.CLEAR_SCREEN)
        self._stdout.flush()

    def _printAll(self):
        self._printHeader(flush = False)
        self._printLines(flush = False)        
        self._printCursor()
        
    def _printHeader(self, flush:bool = True, message: str = None):
        filename = ""
        if self._filename != None:
            filename = self._filename 
        else: 
            filename = "<none>"
        if self._readonly:
            filename += " [RO]"
        if self._title == None:
            header1 = f" {filename:} "
        else:
            header1 = f" {self._title} "
        if self._dirty:
            header1 += "*"
        header2 = f" {f"{self._format}, " if self._format else ""}Ln {self._cursor_y + 1}/{len(self._lines)}, Col {self._cursor_x + 1}, {"INS" if self._insert else "OVR"}, {self._encoding}, {self._newline.replace('\n','LF').replace('\r','CR')} "
        header = header1 + (" " * (self._cols - len(header1) - len(header2) )) + header2  
        # message
        if message != None:
            header = " " + message + (" " * (self._cols - len(message) - 2))

        # print
        self._stdout.write(Sequences.CURSOR_HIDE)
        
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1))
        self._stdout.write(Sequences.BG_WHITE + Sequences.FG_BLACK)
        self._stdout.write(header)
        self._stdout.write(Sequences.RESET)
        self._stdout.write(Sequences.CURSOR_SHOW)
        if flush:
            self._stdout.flush()

    def _printCursor(self, flush = True):
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1 + self._cursor_x - self._offset_x, 1 + 1 + self._cursor_y - self._offset_y))
        if flush:
            self._stdout.flush()

    def _printLine(self, index, flush = True):
        if index >= len(self._lines):
            line = ""
        else:
            line = self._lines[index].replace('\t', "    ")
        if len(line) <= self._offset_x:
            line = ""
        else:
            line = line[self._offset_x:]
        if len(line) > self._cols:
            line = line[:self._cols]

        line_len = len(line)

        self._stdout.write(Sequences.CURSOR_HIDE)
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1 + 1 + index - self._offset_y))

        # selected
        if self._select_x != None:
            line = self._colorizeLine(line, index)

        if line_len < self._cols:
            line += " " * (self._cols - line_len)
        if index == self._rows - 1:
            line = line[:line_len - 1]
        
        # highlight
        line = self._hightlight(line)
        
        # current line hightlight
        if index == self._cursor_y:
            line = Sequences.bg_color_fromrgb("#222222") + line + Sequences.RESET

        # print
        self._stdout.write(line)
        self._stdout.write(Sequences.CURSOR_SHOW)
        self._printCursor(flush = flush)

    def _printLines(self, flush = True):
        self._stdout.write(Sequences.CURSOR_HIDE)
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1,2))
        self._stdout.write(Sequences.RESET)
        for y in range(self._rows - 1):
            line = None
            # cut line
            if len(self._lines) <= self._offset_y + y:
                line = ""
            else:
                line = self._lines[self._offset_y + y]
            if len(line) <= self._offset_x:
                line = ""
            else:
                line = line[self._offset_x:]
            if len(line) > self._cols:
                line = line[:self._cols]

            # remember line len
            line_len = len(line)

            # colorize
            line = self._colorizeLine(line, self._offset_y + y)

            # append spaces to end of line
            if line_len < self._cols:
                line += " " * (self._cols - line_len)

            # add new line if required
            if y < self._rows - 1:
                line += "\n"

            # write 
            if y == self._rows - 1 - 1:
                line = line[:len(line) - 1]

            # hightlight
            line = self._hightlight(line)  

            # current line hightlight
            if y == self._cursor_y:
                line = Sequences.bg_color_fromrgb("#222222") + line + Sequences.RESET

            # write line
            self._stdout.write(line)

        self._printCursor(flush = False)
        self._stdout.write(Sequences.CURSOR_SHOW)
        if flush:
            self._stdout.flush()

    def _info(self, message: str) -> str:
        editor = XEditor()
        editor.editText(message, format = "md", readonly = True, use_quit_escape = True, title = "Help: press ESC to quit", use_buffers = False)
        self._printAll()        
    
    def _question(self, message: str) -> str:
        self._stdout.write(Sequences.BG_WHITE + Sequences.FG_BLACK)
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1))
        self._stdout.write(" " * self._cols)
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1))
        self._stdout.write(Sequences.BG_WHITE + Sequences.FG_BLACK)
        result = None
        try:
            result = input(message + " ")
        except KeyboardInterrupt:
            result = None
        self._stdout.write(Sequences.RESET)
        self._printAll()
        return result

    def _questionYesNo(self, message: str) -> str:
        self._stdout.write(Sequences.BG_WHITE + Sequences.FG_BLACK)
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1))
        self._stdout.write(" " * (self._cols - 1))
        self._stdout.write(Sequences.SET_CURSOR_POSITION_X_Y.format(1, 1))
        self._stdout.write(Sequences.BG_WHITE + Sequences.FG_BLACK)
        result = None
        print(" " + message + " ", end='', flush=True)
        key = ""
        while True:
            key = readKey()
            if key == Keys.CTRL_C:
                result = None
                break
            if key == Keys.ESCAPE:
                result = None
                break
            key = key.lower()
            if key == "y" or key == "n":
                result = key
                break
        self._stdout.write(Sequences.RESET)
        self._printAll()
        return result

    def _show_error(self, message: str) -> str:
        self._printHeader(message = message )
        self._printCursor()

    def _colorizeLine(self, line, index):
        if self._select_x != None:
            bg_color = Sequences.BG_BLUE
            bg_color = Sequences.bg_color_fromrgb("#444444")
            reset = Sequences.RESET
            x1 = self._select_x - self._offset_x
            y1 = self._select_y
            x2 = self._cursor_x - self._offset_x
            y2 = self._cursor_y
            # reorder dots
            if y1 < y2:
                pass
            elif y1 == y2:
                if x1 > x2:
                    x1,x2 = x2,x1    
            elif y1 > y2:
                x1,x2 = x2,x1
                y1,y2 = y2,y1
            # print
            if y1 < index:
                if y2 < index:
                    pass
                elif y2 == index:
                    line = bg_color + line[:x2] + reset + line[x2:]
                elif y2 > index:
                    line = bg_color + line + reset
            elif y1 == index:
                if y1 == y2:
                    line = line[:x1] + bg_color +  line[x1:x2] + reset + line[x2:]
                else:
                    line = line[:x1] + bg_color + line[x1:] + reset
            elif y1 > index:
                pass
        return line
    
    def _validateFormat(self):
        if self._format == "json":
            # json
            text = self._newline.join(self._lines)
            try:
                json.loads(text)
                return True  
            except json.JSONDecodeError as e:
                self._show_error(f"Invalid json: {e}")
                return False 
        elif self._format == "jsonc":
            # jsonc
            text = self._newline.join(self._lines)
            try:
                json5.loads(text)
                return True  
            except Exception as e:
                self._show_error(f"Invalid jsonc: {e}")
                return False 
        elif self._format == "password":
            # password
            text = self._newline.join(self._lines)
            if text.strip() == "":
                self._show_error(f"Invalid password: password cannot be empty")
                return False
        elif self._format == "env":
            # env
            for line in self._lines:
                if line.strip() == "" or line.strip().startswith("#"):
                    continue
                elif "=" not in line:
                    self._show_error(f"Invalid env: missing = in line '{line}'")
                    return False
        elif self._format == "xml":
            # xml
            text = self._newline.join(self._lines)
            try:
                xml.etree.ElementTree.fromstring(text)
                return True
            except ET.ParseError as e:
                self._show_error(f"Invalid xml: {e}")
                return False
        elif self._format == "yaml" or self._format == "yml":
            # yaml
            text = self._newline.join(self._lines)
            try:
                yaml.safe_load(text)
                return True
            except yaml.YAMLError as e:
                self._show_error(f"Invalid yaml: {e}")
                return False
        elif self._format == "md":
            # md
            text = self._newline.join(self._lines)
            
        return True

    # loop                
    def _loop(self):
        # clear
        self._clear()
        # highlighter
        if self._format == "env":
            self._hightlight = hightlight_env
        elif self._format == "md":
            self._hightlight = hightlight_md
        elif self._format == "json" or self._format == "jsonc":
            self._hightlight = hightlight_json
        else:
            self._hightlight = hightlight_none
        # set cursor style
        self._stdout.write(Sequences.CURSOR_SHAPE_BLINKING_BLOCK)
        # prepare
        self._printAll()
        self._printLine(0)
        # loop
        while not self._stop:
            # read key
            key = readKey()            

            # check for size changed
            current_size = os.get_terminal_size()            
            if self._rows != current_size.lines or self._cols != current_size.columns:
                self._cols , self._rows = os.get_terminal_size()
                self._printAll()

            # control
            if key == Keys.CTRL_A:
                self.selectAll()
            elif key == Keys.CTRL_C:
                self.copy()
            elif key == Keys.CTRL_Q:
                self.quit()
            elif key == Keys.CTRL_S:
                self.save()
            elif key == Keys.CTRL_X:
                self.cutAndCopy()
            elif key == Keys.CTRL_Z:
                self.undo()
            elif key == Keys.CTRL_Y:
                self.redo()
            elif key == Keys.CTRL_F:
                self.find()
            elif key == Keys.CTRL_G:
                self.goto()
            elif key == Keys.F1:
                self.help()
            elif key == Keys.F2:
                pass
            elif key == Keys.F3:
                if self._keyword != None:
                    self.findNext()
                else:
                    self.find()
            elif key == Keys.SHIFT_F3:
                if self._keyword != None:
                    self.findPrevious()
                else:
                    self.find(True)

            # arrows
            elif key == Keys.RIGHT_ARROW:
                self.right()
            elif key == Keys.LEFT_ARROW:
                self.left()
            elif key == Keys.UP_ARROW:
                self.up()
            elif key == Keys.DOWN_ARROW:
                self.down()
            elif key == Keys.PAGE_UP:
                self.pageUp()
            elif key == Keys.PAGE_DOWN:
                self.pageDown()
            elif key == Keys.HOME_ARROW:
                self.home()
            elif key == Keys.END_ARROW:
                self.end()

            # control
            elif key == Keys.CTRL_RIGHT_ARROW:
                self.rightWord()
            elif key == Keys.CTRL_LEFT_ARROW:
                self.leftWord()
            elif key == Keys.CTRL_UP_ARROW:
                self.scrollUp()
            elif key == Keys.CTRL_DOWN_ARROW:
                self.scrollDown()

            elif key == Keys.CTRL_HOME_ARROW:
                self.scrollTop()
            elif key == Keys.CTRL_END_ARROW:
                self.scrollBottom()

            # select
            elif key == Keys.SHIFT_RIGHT_ARROW:
                self.right(True)
            elif key == Keys.SHIFT_LEFT_ARROW:
                self.left(True)
            elif key == Keys.SHIFT_UP_ARROW:
                self.up(True)
            elif key == Keys.SHIFT_DOWN_ARROW:
                self.down(True)
            elif key == Keys.SHIFT_PAGE_UP:
                self.pageUp(True)
            elif key == Keys.SHIFT_PAGE_DOWN:
                self.pageDown(True)
            elif key == Keys.SHIFT_HOME_ARROW:
                self.home(True)
            elif key == Keys.SHIFT_END_ARROW:
                self.end(True)
            elif key == Keys.CTRL_SHIFT_RIGHT_ARROW:
                self.rightWord(True)
            elif key == Keys.CTRL_SHIFT_LEFT_ARROW:
                self.leftWord(True)
            elif key == Keys.CTRL_SHIFT_UP_ARROW:
                self.up(True)
            elif key == Keys.CTRL_SHIFT_DOWN_ARROW:
                self.down(True)

            # other
            elif key == Keys.ESCAPE:
                self.escape()
            elif key == Keys.ENTER:
                self.enter()
            elif key == Keys.BACKSPACE:
                self.backspace()
            elif key == Keys.INSERT:
                self.insert()
            elif key == Keys.DELETE:
                self.delete()
            elif key == Keys.TAB:
                self.tab()
            elif key == Keys.SHIFT_TAB:
                self.untab()

            # keypress
            else:
                self.keypress(key)

