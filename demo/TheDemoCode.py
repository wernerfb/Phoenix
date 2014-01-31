#!/bin/env python
#----------------------------------------------------------------------------
# Name:         TheDemoCode.py
# Purpose:      Demonstrates widgets/controls available with wxPython
#
# Author:       Based on Main.py by Robin Dunn
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 1999 by Total Control Software
# Licence:      wxWindows license
# Tags:         phoenix-port
#----------------------------------------------------------------------------

# TODO: need to update all this
#
# FIXME List:
# * Problems with flickering related to ERASE_BACKGROUND
#     and the splitters. Might be a problem with this 2.5 beta...?
#     UPDATE: can't see on 2.5.2 GTK - maybe just a faster machine :)
# * Demo Code menu?
# * Annoying switching between tabs and resulting flicker
#     how to replace a page in the notebook without deleting/adding?
#     Where is SetPage!? tried freeze...tried reparent of dummy panel....
#     AG: It looks like this issue is fixed by Freeze()ing and Thaw()ing the
#         main frame and not the notebook

# TODO List:
# * UI design more professional (is the new version more professional?)
# * save file positions (new field in demoModules) (@ LoadDemoSource)
# * Update main overview

# * Why don't we move _treeList into a separate module

# =====================
# = EXTERNAL Packages =
# =====================
# In order to let a package (like AGW) be included in the wxPython demo,
# the package owner should create a sub-directory of the wxPython demo folder
# in which all the package's demos should live. In addition, the sub-folder
# should contain a Python file called __demo__.py which, when imported, should
# contain the following methods:
#
# * GetDemoBitmap: returns the bitmap to be used in the wxPython demo tree control
#   in a PyEmbeddedImage format;
# * GetRecentAdditions: returns a list of demos which will be displayed under the
#   "Recent Additions/Updates" tree item. This list should be a subset (or the full
#   set) of the package's demos;
# * GetDemos: returns a tuple. The first item of the tuple is the package's name
#   as will be displayed in the wxPython demo tree, right after the "Custom Controls"
#   item. The second element of the tuple is the list of demos for the external package.
# * GetOverview: returns a wx.html-ready representation of the package's documentation.
#
# Please see the __demo__.py file in the demo/agw/ folder for an example.
# Last updated: Andrea Gavana, 20 Oct 2008, 18.00 GMT

import sys
import os
import time
import traceback
import re
import shutil
from threading import Thread

import wx
import wx.adv
import wx.lib.agw.aui as aui
import wx.html
from wx.lib.msgpanel import MessagePanel
from wx.adv import TaskBarIcon as TaskBarIcon
from wx.adv import SplashScreen as SplashScreen
import wx.lib.mixins.inspection

import wx.lib.six as six
from wx.lib.six import exec_

import version
import images

#---------------------------------------------------------------------------

USE_CUSTOMTREECTRL = False
DEFAULT_PERSPECTIVE = "Default Perspective"


#---------------------------------------------------------------------------
# Show how to derive a custom wxLog class

class MyLog(wx.Log):
    def __init__(self, textCtrl, logTime=0):
        wx.Log.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogText(self, message):
        if self.tc:
            self.tc.AppendText(message + '\n')


#---------------------------------------------------------------------------
# A class to be used to display source code in the demo.  Try using the
# wxSTC in the StyledTextCtrl_2 sample first, fall back to wxTextCtrl
# if there is an error, such as the stc module not being present.
#

try:
    ##raise ImportError     # for testing the alternate implementation
    from wx import stc
    from StyledTextCtrl_2 import PythonSTC

    class DemoCodeEditor(PythonSTC):
        def __init__(self, parent, style=wx.BORDER_NONE):
            PythonSTC.__init__(self, parent, -1, style=style)
            self.SetUpEditor()

        # Some methods to make it compatible with how the wxTextCtrl is used
        def SetValue(self, value):
            # if wx.USE_UNICODE:
                # value = value.decode('iso8859_1')
            val = self.GetReadOnly()
            self.SetReadOnly(False)
            self.SetText(value)
            self.EmptyUndoBuffer()
            self.SetSavePoint()
            self.SetReadOnly(val)

        def SetEditable(self, val):
            self.SetReadOnly(not val)

        def IsModified(self):
            return self.GetModify()

        def Clear(self):
            self.ClearAll()

        def SetInsertionPoint(self, pos):
            self.SetCurrentPos(pos)
            self.SetAnchor(pos)

        def ShowPosition(self, pos):
            line = self.LineFromPosition(pos)
            #self.EnsureVisible(line)
            self.GotoLine(line)

        def GetLastPosition(self):
            return self.GetLength()

        def GetPositionFromLine(self, line):
            return self.PositionFromLine(line)

        def GetRange(self, start, end):
            return self.GetTextRange(start, end)

        def GetSelection(self):
            return self.GetAnchor(), self.GetCurrentPos()

        def SetSelection(self, start, end):
            self.SetSelectionStart(start)
            self.SetSelectionEnd(end)

        def SelectLine(self, line):
            start = self.PositionFromLine(line)
            end = self.GetLineEndPosition(line)
            self.SetSelection(start, end)

        def SetUpEditor(self):
            """
            This method carries out the work of setting up the demo editor.
            It's seperate so as not to clutter up the init code.
            """
            import keyword

            self.SetLexer(stc.STC_LEX_PYTHON)
            self.SetKeyWords(0, " ".join(keyword.kwlist))

            # Enable folding
            self.SetProperty("fold", "1")

            # Highlight tab/space mixing (shouldn't be any)
            self.SetProperty("tab.timmy.whinge.level", "1")

            # Set left and right margins
            self.SetMargins(2, 2)

            # Set up the numbers in the margin for margin #1
            self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
            # Reasonable value for, say, 4-5 digits using a mono font (40 pix)
            self.SetMarginWidth(1, 40)

            # Indentation and tab stuff
            self.SetIndent(4)                 # Proscribed indent size for wx
            self.SetIndentationGuides(True)   # Show indent guides
            self.SetBackSpaceUnIndents(True)  # Backspace unindents rather than delete 1 space
            self.SetTabIndents(True)          # Tab key indents
            self.SetTabWidth(4)               # Proscribed tab size for wx
            self.SetUseTabs(False)            # Use spaces rather than tabs, or
                                              # TabTimmy will complain!
            # White space
            self.SetViewWhiteSpace(False)   # Don't view white space

            # EOL: Since we are loading/saving ourselves, and the
            # strings will always have \n's in them, set the STC to
            # edit them that way.
            self.SetEOLMode(wx.stc.STC_EOL_LF)
            self.SetViewEOL(False)

            # No right-edge mode indicator
            self.SetEdgeMode(stc.STC_EDGE_NONE)

            # Setup a margin to hold fold markers
            self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
            self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
            self.SetMarginSensitive(2, True)
            self.SetMarginWidth(2, 12)

            # and now set up the fold markers
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "black")
            self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "black")

            # Global default style
            if wx.Platform == '__WXMSW__':
                self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                                  'fore:#000000,back:#FFFFFF,face:Courier New')
            elif wx.Platform == '__WXMAC__':
                # TODO: if this looks fine on Linux too, remove the Mac-specific case
                # and use this whenever OS != MSW.
                self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                                  'fore:#000000,back:#FFFFFF,face:Monaco')
            else:
                defsize = wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT).GetPointSize()
                self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                                  'fore:#000000,back:#FFFFFF,face:Courier,size:%d' % defsize)

            # Clear styles and revert to default.
            self.StyleClearAll()

            # Following style specs only indicate differences from default.
            # The rest remains unchanged.

            # Line numbers in margin
            self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, 'fore:#000000,back:#99A9C2')
            # Highlighted brace
            self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, 'fore:#00009D,back:#FFFF00')
            # Unmatched brace
            self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, 'fore:#00009D,back:#FF0000')
            # Indentation guide
            self.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")

            # Python styles
            self.StyleSetSpec(wx.stc.STC_P_DEFAULT, 'fore:#000000')
            # Comments
            self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, 'fore:#008000,back:#F0FFF0')
            self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#F0FFF0')
            # Numbers
            self.StyleSetSpec(wx.stc.STC_P_NUMBER, 'fore:#008080')
            # Strings and characters
            self.StyleSetSpec(wx.stc.STC_P_STRING, 'fore:#800080')
            self.StyleSetSpec(wx.stc.STC_P_CHARACTER, 'fore:#800080')
            # Keywords
            self.StyleSetSpec(wx.stc.STC_P_WORD, 'fore:#000080,bold')
            # Triple quotes
            self.StyleSetSpec(wx.stc.STC_P_TRIPLE, 'fore:#800080,back:#FFFFEA')
            self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, 'fore:#800080,back:#FFFFEA')
            # Class names
            self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, 'fore:#0000FF,bold')
            # Function names
            self.StyleSetSpec(wx.stc.STC_P_DEFNAME, 'fore:#008080,bold')
            # Operators
            self.StyleSetSpec(wx.stc.STC_P_OPERATOR, 'fore:#800000,bold')
            # Identifiers. I leave this as not bold because everything seems
            # to be an identifier if it doesn't match the above criterae
            self.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, 'fore:#000000')

            # Caret color
            self.SetCaretForeground("BLUE")
            # Selection background
            self.SetSelBackground(1, '#66CCFF')

            self.SetSelBackground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
            self.SetSelForeground(True, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        def RegisterModifiedEvent(self, eventHandler):
            self.Bind(wx.stc.EVT_STC_CHANGE, eventHandler)


except ImportError:
    class DemoCodeEditor(wx.TextCtrl):
        def __init__(self, parent):
            wx.TextCtrl.__init__(self, parent, -1, style=wx.TE_MULTILINE |
                                 wx.HSCROLL | wx.TE_RICH2 | wx.TE_NOHIDESEL)

        def RegisterModifiedEvent(self, eventHandler):
            self.Bind(wx.EVT_TEXT, eventHandler)

        def SetReadOnly(self, flag):
            self.SetEditable(not flag)
            # NOTE: STC already has this method

        def GetText(self):
            return self.GetValue()

        def GetPositionFromLine(self, line):
            return self.XYToPosition(0, line)

        def GotoLine(self, line):
            pos = self.GetPositionFromLine(line)
            self.SetInsertionPoint(pos)
            self.ShowPosition(pos)

        def SelectLine(self, line):
            start = self.GetPositionFromLine(line)
            end = start + self.GetLineLength(line)
            self.SetSelection(start, end)


#---------------------------------------------------------------------------
# Constants for module versions

modOriginal = 0
modModified = 1
modDefault = modOriginal

#---------------------------------------------------------------------------


class DemoCodePanel(wx.Panel):
    """Panel for the 'Demo Code' tab"""
    def __init__(self, parent, mainFrame):
        wx.Panel.__init__(self, parent, size=(1, 1))
        if 'wxMSW' in wx.PlatformInfo:
            self.Hide()
        self.mainFrame = mainFrame
        self.editor = DemoCodeEditor(self)
        self.editor.RegisterModifiedEvent(self.OnCodeModified)

        self.btnSave = wx.Button(self, -1, "Save Changes")
        self.btnRestore = wx.Button(self, -1, "Delete Modified")
        self.btnSave.Enable(False)
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.btnRestore.Bind(wx.EVT_BUTTON, self.OnRestore)

        self.radioButtons = {modOriginal: wx.RadioButton(self, -1, "Original", style=wx.RB_GROUP),
                             modModified: wx.RadioButton(self, -1, "Modified")}

        self.controlBox = wx.BoxSizer(wx.HORIZONTAL)
        self.controlBox.Add(wx.StaticText(self, -1, "Active Version:"), 0,
                            wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        for modID, radioButton in self.radioButtons.items():
            self.controlBox.Add(radioButton, 0, wx.EXPAND | wx.RIGHT, 5)
            radioButton.modID = modID  # makes it easier for the event handler
            radioButton.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)

        self.controlBox.Add(self.btnSave, 0, wx.RIGHT, 5)
        self.controlBox.Add(self.btnRestore, 0)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.controlBox, 0, wx.EXPAND)
        self.box.Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.box.Add(self.editor, 1, wx.EXPAND)

        self.box.Fit(self)
        self.SetSizer(self.box)

    # Loads a demo from a DemoModules object
    def LoadDemo(self, demoModules):
        self.demoModules = demoModules
        if (modDefault == modModified) and demoModules.Exists(modModified):
            demoModules.SetActive(modModified)
        else:
            demoModules.SetActive(modOriginal)
        self.radioButtons[demoModules.GetActiveID()].Enable(True)
        self.ActiveModuleChanged()

    def ActiveModuleChanged(self):
        self.LoadDemoSource(self.demoModules.GetSource())
        self.UpdateControlState()
        self.mainFrame.Freeze()
        self.ReloadDemo()
        self.mainFrame.Thaw()

    def LoadDemoSource(self, source):
        self.editor.Clear()
        self.editor.SetValue(source)
        self.JumpToLine(0)
        self.btnSave.Enable(False)

    def JumpToLine(self, line, highlight=False):
        self.editor.GotoLine(line)
        self.editor.SetFocus()
        if highlight:
            self.editor.SelectLine(line)

    def UpdateControlState(self):
        active = self.demoModules.GetActiveID()
        # Update the radio/restore buttons
        for moduleID in self.radioButtons:
            btn = self.radioButtons[moduleID]
            if moduleID == active:
                btn.SetValue(True)
            else:
                btn.SetValue(False)

            if self.demoModules.Exists(moduleID):
                btn.Enable(True)
                if moduleID == modModified:
                    self.btnRestore.Enable(True)
            else:
                btn.Enable(False)
                if moduleID == modModified:
                    self.btnRestore.Enable(False)

    def OnRadioButton(self, event):
        radioSelected = event.GetEventObject()
        modSelected = radioSelected.modID
        if modSelected != self.demoModules.GetActiveID():
            busy = wx.BusyInfo("Reloading demo module...")
            self.demoModules.SetActive(modSelected)
            self.ActiveModuleChanged()

    def ReloadDemo(self):
        if self.demoModules.name != __name__:
            self.mainFrame.RunModule()

    def OnCodeModified(self, event):
        self.btnSave.Enable(self.editor.IsModified())

    def OnSave(self, event):
        if self.demoModules.Exists(modModified):
            if self.demoModules.GetActiveID() == modOriginal:
                overwriteMsg = "You are about to overwrite an already existing modified copy\n" + \
                               "Do you want to continue?"
                dlg = wx.MessageDialog(self, overwriteMsg, "wxPython Demo",
                                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
                result = dlg.ShowModal()
                if result == wx.ID_NO:
                    return
                dlg.Destroy()

        self.demoModules.SetActive(modModified)
        modifiedFilename = GetModifiedFilename(self.demoModules.name)

        # Create the demo directory if one doesn't already exist
        if not os.path.exists(GetModifiedDirectory()):
            try:
                os.makedirs(GetModifiedDirectory())
                if not os.path.exists(GetModifiedDirectory()):
                    wx.LogMessage("BUG: Created demo directory but it still doesn't exist")
                    raise AssertionError
            except:
                wx.LogMessage("Error creating demo directory: %s" % GetModifiedDirectory())
                return
            else:
                wx.LogMessage("Created directory for modified demos: %s" % GetModifiedDirectory())

        # Save
        f = open(modifiedFilename, "wt")
        source = self.editor.GetText()
        try:
            f.write(source)
        finally:
            f.close()

        busy = wx.BusyInfo("Reloading demo module...")
        self.demoModules.LoadFromFile(modModified, modifiedFilename)
        self.ActiveModuleChanged()

    def OnRestore(self, event):  # Handles the "Delete Modified" button
        modifiedFilename = GetModifiedFilename(self.demoModules.name)
        self.demoModules.Delete(modModified)
        os.unlink(modifiedFilename)  # Delete the modified copy
        busy = wx.BusyInfo("Reloading demo module...")

        self.ActiveModuleChanged()

#---------------------------------------------------------------------------


def opj(path):
    """Convert paths to the platform-specific separator"""
    st = os.path.join(*tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


def GetDataDir():
    """
    Return the standard location on this platform for application data
    """
    sp = wx.StandardPaths.Get()
    return sp.GetUserDataDir()


def GetModifiedDirectory():
    """
    Returns the directory where modified versions of the demo files
    are stored
    """
    return os.path.join(GetDataDir(), "modified")


def GetModifiedFilename(name):
    """
    Returns the filename of the modified version of the specified demo
    """
    if not name.endswith(".py"):
        name = name + ".py"
    return os.path.join(GetModifiedDirectory(), name)


def GetOriginalFilename(name):
    """
    Returns the filename of the original version of the specified demo
    """
    if not name.endswith(".py"):
        name = name + ".py"

    if os.path.isfile(name):
        return name

    originalDir = os.getcwd()
    listDir = os.listdir(originalDir)
    # Loop over the content of the demo directory
    for item in listDir:
        if not os.path.isdir(item):
            # Not a directory, continue
            continue
        dirFile = os.listdir(item)
        # See if a file called "name" is there
        if name in dirFile:
            return os.path.join(item, name)

    # We must return a string...
    return ""


def DoesModifiedExist(name):
    """Returns whether the specified demo has a modified copy"""
    if os.path.exists(GetModifiedFilename(name)):
        return True
    else:
        return False


def GetConfig():
    if not os.path.exists(GetDataDir()):
        os.makedirs(GetDataDir())

    config = wx.FileConfig(
        localFilename=os.path.join(GetDataDir(), "options"))
    return config

#---------------------------------------------------------------------------


class ModuleDictWrapper(object):
    """Emulates a module with a dynamically compiled __dict__"""
    def __init__(self, dict):
        self.dict = dict

    def __getattr__(self, name):
        if name in self.dict:
            return self.dict[name]
        else:
            raise AttributeError


class DemoModules(object):
    """
    Dynamically manages the original/modified versions of a demo
    module
    """
    def __init__(self, name):
        self.modActive = -1
        self.name = name

        #              (dict , source ,  filename , description   , error information )
        #              (  0  ,   1    ,     2     ,      3        ,          4        )
        self.modules = [[dict(), "", "", "<original>", None],
                        [dict(), "", "", "<modified>", None]]

        getcwd = os.getcwd if six.PY3 else os.getcwdu
        for i in [modOriginal, modModified]:
            self.modules[i][0]['__file__'] = \
                os.path.join(getcwd(), GetOriginalFilename(name))

        # load original module
        self.LoadFromFile(modOriginal, GetOriginalFilename(name))
        self.SetActive(modOriginal)

        # load modified module (if one exists)
        if DoesModifiedExist(name):
            self.LoadFromFile(modModified, GetModifiedFilename(name))

    def LoadFromFile(self, modID, filename):
        self.modules[modID][2] = filename
        file = open(filename, "rt")
        self.LoadFromSource(modID, file.read())
        file.close()

    def LoadFromSource(self, modID, source):
        self.modules[modID][1] = source
        self.LoadDict(modID)

    def LoadDict(self, modID):
        if self.name != __name__:
            source = self.modules[modID][1]
            description = self.modules[modID][2]
            if six.PY2:
                description = description.encode(sys.getfilesystemencoding())

            try:
                code = compile(source, description, "exec")
                exec_(code, self.modules[modID][0])
            except:
                self.modules[modID][4] = DemoError(sys.exc_info())
                self.modules[modID][0] = None
            else:
                self.modules[modID][4] = None

    def SetActive(self, modID):
        if modID != modOriginal and modID != modModified:
            raise LookupError
        else:
            self.modActive = modID

    def GetActive(self):
        dict = self.modules[self.modActive][0]
        if dict is None:
            return None
        else:
            return ModuleDictWrapper(dict)

    def GetActiveID(self):
        return self.modActive

    def GetSource(self, modID=None):
        if modID is None:
            modID = self.modActive
        return self.modules[modID][1]

    def GetFilename(self, modID=None):
        if modID is None:
            modID = self.modActive
        return self.modules[self.modActive][2]

    def GetErrorInfo(self, modID=None):
        if modID is None:
            modID = self.modActive
        return self.modules[self.modActive][4]

    def Exists(self, modID):
        return self.modules[modID][1] != ""

    def UpdateFile(self, modID=None):
        """Updates the file from which a module was loaded
        with (possibly updated) source"""
        if modID is None:
            modID = self.modActive

        source = self.modules[modID][1]
        filename = self.modules[modID][2]

        try:
            file = open(filename, "wt")
            file.write(source)
        finally:
            file.close()

    def Delete(self, modID):
        if self.modActive == modID:
            self.SetActive(0)

        self.modules[modID][0] = None
        self.modules[modID][1] = ""
        self.modules[modID][2] = ""


#---------------------------------------------------------------------------


class DemoError(object):
    """Wraps and stores information about the current exception"""
    def __init__(self, exc_info):
        import copy

        excType, excValue = exc_info[:2]
        # traceback list entries: (filename, line number, function name, text)
        self.traceback = traceback.extract_tb(exc_info[2])

        # --Based on traceback.py::format_exception_only()--
        if isinstance(excType, type):
            self.exception_type = excType.__name__
        else:
            self.exception_type = excType

        # If it's a syntax error, extra information needs
        # to be added to the traceback
        if excType is SyntaxError:
            try:
                msg, (filename, lineno, self.offset, line) = excValue
            except:
                pass
            else:
                if not filename:
                    filename = "<string>"
                line = line.strip()
                self.traceback.append((filename, lineno, "", line))
                excValue = msg
        try:
            self.exception_details = str(excValue)
        except:
            self.exception_details = "<unprintable %s object>" & type(excValue).__name__

        del exc_info

    def __str__(self):
        ret = "Type %s \n \
        Traceback: %s \n \
        Details  : %s" % (str(self.exception_type), str(self.traceback), self.exception_details)
        return ret

#---------------------------------------------------------------------------


class DemoErrorPanel(wx.Panel):
    """Panel put into the demo tab when the demo fails to run due  to errors"""

    def __init__(self, parent, codePanel, demoError, log):
        wx.Panel.__init__(self, parent, -1)
        self.codePanel = codePanel
        self.nb = parent
        self.log = log

        self.box = wx.BoxSizer(wx.VERTICAL)

        # Main Label
        self.box.Add(wx.StaticText(self, -1, "An error has occurred while trying to run the demo"),
                     0, wx.ALIGN_CENTER | wx.TOP, 10)

        # Exception Information
        boxInfo = wx.StaticBox(self, -1, "Exception Info")
        boxInfoSizer = wx.StaticBoxSizer(boxInfo, wx.VERTICAL)  # Used to center the grid within the box
        boxInfoGrid = wx.FlexGridSizer(cols=2)
        textFlags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.TOP
        boxInfoGrid.Add(wx.StaticText(self, -1, "Type: "), 0, textFlags, 5)
        boxInfoGrid.Add(wx.StaticText(self, -1, str(demoError.exception_type)), 0, textFlags, 5)
        boxInfoGrid.Add(wx.StaticText(self, -1, "Details: "), 0, textFlags, 5)
        boxInfoGrid.Add(wx.StaticText(self, -1, demoError.exception_details), 0, textFlags, 5)
        boxInfoSizer.Add(boxInfoGrid, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.box.Add(boxInfoSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Set up the traceback list
        # This one automatically resizes last column to take up remaining space
        from ListCtrl import TestListCtrl
        self.list = TestListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.list.InsertColumn(0, "Filename")
        self.list.InsertColumn(1, "Line", wx.LIST_FORMAT_RIGHT)
        self.list.InsertColumn(2, "Function")
        self.list.InsertColumn(3, "Code")
        self.InsertTraceback(self.list, demoError.traceback)
        self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.box.Add(wx.StaticText(self, -1, "Traceback:"),
                     0, wx.ALIGN_CENTER | wx.TOP, 5)
        self.box.Add(self.list, 1, wx.GROW | wx.ALIGN_CENTER | wx.ALL, 5)
        self.box.Add(wx.StaticText(self, -1, "Entries from the demo module are shown in blue\n"
                                           + "Double-click on them to go to the offending line"),
                     0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

        self.box.Fit(self)
        self.SetSizer(self.box)

    def InsertTraceback(self, list, traceback):
        #Add the traceback data
        for x in range(len(traceback)):
            data = traceback[x]
            list.InsertItem(x, os.path.basename(data[0]))  # Filename
            list.SetItem(x, 1, str(data[1]))               # Line
            list.SetItem(x, 2, str(data[2]))               # Function
            list.SetItem(x, 3, str(data[3]))               # Code

            # Check whether this entry is from the demo module
            if data[0] == "<original>" or data[0] == "<modified>":  # FIXME: make more generalised
                self.list.SetItemData(x, int(data[1]))  # Store line number for easy access
                # Give it a blue colour
                item = self.list.GetItem(x)
                item.SetTextColour(wx.BLUE)
                self.list.SetItem(item)
            else:
                self.list.SetItemData(x, -1)  # Editor can't jump into this one's code

    def OnItemSelected(self, event):
        # This occurs before OnDoubleClick and can be used to set the
        # currentItem. OnDoubleClick doesn't get a wxListEvent....
        self.currentItem = event.Index
        event.Skip()

    def OnDoubleClick(self, event):
        # If double-clicking on a demo's entry, jump to the line number
        line = self.list.GetItemData(self.currentItem)
        if line != -1:
            self.nb.SetSelection(1)  # Switch to the code viewer tab
            wx.CallAfter(self.codePanel.JumpToLine, line - 1, True)
        event.Skip()

#---------------------------------------------------------------------------


class wxPythonDemo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.mgr = aui.AuiManager()
        self.mgr.SetManagedWindow(self)

        self.loaded = False
        self.cwd = os.getcwd()
        self.curOverview = ""
        self.demoPage = None
        self.codePage = None
        self.firstTime = True
        self.finddlg = None

        self.otherWin = None

        self.allowAuiFloating = False

        # Create a Notebook
        self.nb = wx.Notebook(self, -1, style=wx.CLIP_CHILDREN)
        imgList = wx.ImageList(16, 16)
        for png in ["overview", "code", "demo"]:
            bmp = images.catalog[png].GetBitmap()
            imgList.Add(bmp)
        for indx in range(9):
            bmp = images.catalog["spinning_nb%d" % indx].GetBitmap()
            imgList.Add(bmp)

        self.nb.AssignImageList(imgList)

        self.finddata = wx.FindReplaceData()
        self.finddata.SetFlags(wx.FR_DOWN)

        self.ovr = wx.html.HtmlWindow(self.nb, -1)
        self.nb.AddPage(self.ovr, "Overview", imageId=0)

        if "gtk2" in wx.PlatformInfo:
            self.ovr.SetStandardFonts()

        # Set up a log window
        self.log = wx.TextCtrl(self, -1,
                               style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        if wx.Platform == "__WXMAC__":
            self.log.MacCheckSpelling(False)

        # Set the wxWindows log target to be this textctrl
        #wx.Log.SetActiveTarget(wx.LogTextCtrl(self.log))

        # But instead of the above we want to show how to use our own wx.Log class
        wx.Log.SetActiveTarget(MyLog(self.log))

        # for serious debugging
        #wx.Log.SetActiveTarget(wx.LogStderr())
        #wx.Log.SetTraceMask(wx.TraceMessages)

        # select initial items
        self.nb.SetSelection(0)

        # Use the aui manager to set up everything
        self.mgr.AddPane(self.nb, aui.AuiPaneInfo().CenterPane().Name("Notebook"))
        self.mgr.AddPane(self.log,
                         aui.AuiPaneInfo().
                         Bottom().BestSize((-1, 150)).
                         MinSize((-1, 140)).
                         Floatable(self.allowAuiFloating).FloatingSize((500, 160)).
                         Caption("Demo Log Messages").
                         CloseButton(False).
                         Name("LogWindow"))

        self.mgr.Update()

        self.mgr.SetAGWFlags(self.mgr.GetAGWFlags() ^ aui.AUI_MGR_TRANSPARENT_DRAG)

    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)

    def write(self, txt):
        self.WriteText(txt)

    def LoadDemo(self, demoName):
        # TODO: update to figure out where demo is, maybe create folders 'core', 'dataview' etc
        try:
            wx.BeginBusyCursor()
            self.Freeze()

            os.chdir(self.cwd)
            self.ShutdownDemoModule()

            if os.path.exists(GetOriginalFilename(demoName)):
                wx.LogMessage("Loading demo %s.py..." % demoName)
                self.demoModules = DemoModules(demoName)
                self.LoadDemoSource()

            else:

                package, overview = LookForExternals(self.externalDemos, demoName)

                if package:
                    wx.LogMessage("Loading demo %s.py..." % ("%s/%s" % (package, demoName)))
                    self.demoModules = DemoModules("%s/%s" % (package, demoName))
                    self.LoadDemoSource()
                elif overview:
                    self.SetOverview(demoName, overview)
                    self.codePage = None
                    self.UpdateNotebook(0)
                else:
                    self.SetOverview("wxPython", mainOverview)
                    self.codePage = None
                    self.UpdateNotebook(0)

        finally:
            wx.EndBusyCursor()
            self.Thaw()

    def LoadDemoSource(self):
        self.codePage = None
        self.codePage = DemoCodePanel(self.nb, self)
        self.codePage.LoadDemo(self.demoModules)

    def RunModule(self):
        """Runs the active module"""

        module = self.demoModules.GetActive()
        self.ShutdownDemoModule()
        overviewText = ""

        # o The RunTest() for all samples must now return a window that can
        #   be palced in a tab in the main notebook.
        # o If an error occurs (or has occurred before) an error tab is created.

        if module is not None:
            wx.LogMessage("Running demo module...")
            if hasattr(module, "overview"):
                overviewText = module.overview

            try:
                self.demoPage = module.runTest(self, self.nb, self)
            except:
                self.demoPage = DemoErrorPanel(self.nb, self.codePage,
                                               DemoError(sys.exc_info()), self)

            bg = self.nb.GetThemeBackgroundColour()
            if bg:
                self.demoPage.SetBackgroundColour(bg)

            assert self.demoPage is not None, "runTest must return a window!"

        else:
            # There was a previous error in compiling or exec-ing
            self.demoPage = DemoErrorPanel(self.nb, self.codePage,
                                           self.demoModules.GetErrorInfo(), self)

        self.SetOverview(self.demoModules.name + " Overview", overviewText)

        if self.firstTime:
            # change to the demo page the first time a module is run
            self.UpdateNotebook(2)
            self.firstTime = False
        else:
            # otherwise just stay on the same tab in case the user has changed to another one
            self.UpdateNotebook()

    #---------------------------------------------
    def ShutdownDemoModule(self):
        if self.demoPage:
            # inform the window that it's time to quit if it cares
            if hasattr(self.demoPage, "ShutdownDemo"):
                self.demoPage.ShutdownDemo()
##            wx.YieldIfNeeded() # in case the page has pending events
            self.demoPage = None

    #---------------------------------------------
    def UpdateNotebook(self, select=-1):
        nb = self.nb
        debug = False
        self.Freeze()

        def UpdatePage(page, pageText):
            pageExists = False
            pagePos = -1
            for i in range(nb.GetPageCount()):
                if nb.GetPageText(i) == pageText:
                    pageExists = True
                    pagePos = i
                    break

            if page:
                if not pageExists:
                    # Add a new page
                    nb.AddPage(page, pageText, imageId=nb.GetPageCount())
                    if debug:
                        wx.LogMessage("DBG: ADDED %s" % pageText)
                else:
                    if nb.GetPage(pagePos) != page:
                        # Reload an existing page
                        nb.DeletePage(pagePos)
                        nb.InsertPage(pagePos, page, pageText, imageId=pagePos)
                        if debug:
                            wx.LogMessage("DBG: RELOADED %s" % pageText)
                    else:
                        # Excellent! No redraw/flicker
                        if debug:
                            wx.LogMessage("DBG: SAVED from reloading %s" % pageText)
            elif pageExists:
                # Delete a page
                nb.DeletePage(pagePos)
                if debug:
                    wx.LogMessage("DBG: DELETED %s" % pageText)
            else:
                if debug:
                    wx.LogMessage("DBG: STILL GONE - %s" % pageText)

        if select == -1:
            select = nb.GetSelection()

        UpdatePage(self.codePage, "Demo Code")
        UpdatePage(self.demoPage, "Demo")

        if select >= 0 and select < nb.GetPageCount():
            nb.SetSelection(select)

        self.Thaw()

    def SetOverview(self, name, text):
        self.curOverview = text
        lead = text[:6]
        if lead != '<html>' and lead != '<HTML>':
            text = '<br>'.join(text.split('\n'))
        # if wx.USE_UNICODE:
            # text = text.decode('iso8859_1')
        self.ovr.SetPage(text)
        self.nb.SetPageText(0, os.path.split(name)[1])
