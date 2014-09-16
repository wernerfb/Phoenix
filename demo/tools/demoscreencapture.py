# -*- coding: utf-8 -*-#
#
# Author: Werner F. Bruhin
#
# License: wxPython or equivalent
#
# Idea by: Robin Dunn
# Capture code based on post by John Torres and input by Mike Driscoll
# and Robin and from another post on the subject by Ed Leafe
#

import sys
import os
import importlib
import glob
import traceback
import inspect

import wx
import wx.lib.sized_controls as sc
import wx.lib.mixins.inspection as wit

print("wx Version: %s" % wx.version())

# assumption is that this tool is in demo/tools folder
demoBaseFolder = os.path.join(os.getcwd(), "..")
print("demo base: %s" % demoBaseFolder)

# define sub folders containing demo's for which to capture screen
captFolders = [
               '', # base demo folder
               'agw' # agw demo folder
              ]

# define a base folder to write screen captures too
captBaseFolder = os.path.join(os.getcwd(), "screencaptures")
if not os.path.isdir(captBaseFolder):
    os.mkdir(captBaseFolder)

# lets add a platform subfolder
captBaseFolder = os.path.join(captBaseFolder, wx.PlatformInfo[1])
if not os.path.isdir(captBaseFolder):
    os.mkdir(captBaseFolder)

print("capture to: %s" % captBaseFolder)

pyFiles = []

# files to be ignored
# files which are part of the demo
excluBase = ["Main.py", "run.py", "demo.py", "__demo__.py", 
             "encode_bitmaps.py", "images.py", "infoframe.py",
             "pyTree.py", "template.py", "version.py",
             "ColorPanel.py", "throbImages.py"
             ]

# demo files we don't want to capture as there is no UI or ...
excluDemos = ["AboutBox.py", # About should be enough
              "ActiveXWrapper_Acrobat.py", # PDF sample enough?
              "ActiveXWrapper_IE.py", # PDF sample enough?
              "ActiveX_FlashWindow.py", # PDF sample enough?
              "ActiveX_IEHtmlWindow.py", # PDF sample enough?
              "MDIWindows.py", # individual demos are run instead
              "DelayedResult.py",
              "PythonEvents.py",
              "Threads.py",
              "UIActionSimulator.py",
              "Unicode.py",
              "Validator.py",
              "Wizard.py",
              "WrapSizer.py",
              "XmlResource.py",
              "XmlResourceHandler.py",
              "XmlResourceSubclass.py",
              "XMLtreeview.py",
              "URLDragAndDrop.py",
              "Sizers.py",
              "Sound.py",              
              
              "PersistentControls.py", 

             ]

# demo files which cause problems, crashs, hangs, or ....
# they should get resolved over time
excluProblems = ["ColourDialog.py", # screen is not shown unless use Modal
                 "viewer.py", "viewer_basics.py", # I don't have VTK
                 "PrintDialog.py", # no ".Show" method
                 "PrintFramework.py", # dc.GetSize exception
                 "PageSetupDialog.py", # dc.GetSize exception
                 "TablePrint.py", # dc.GetSize exception
                 "PropertyGrid.py", # crash
                 "EventManager.py", # assertion error
                 "MessageDialog.py", # PyAssertionError due to a huge image size
                 "DirDialog.py", # PyAssertionError due to a huge image size
                 "MacLargeDemo.py", # no RunTest method
                 "AUI_DockingWindowMgr.py", # not supported on Phoenix
                 "AUI_Notebook.py", # not supported on Phoenix
                 "AUI_MDI.py", # not supported on Phoenix
                 ]

# demo files which are called by other demo file
excluSubDemos = ["GridCustEditor.py", "GridCustTable.py",
                 "GridDragable.py", "GridDragAndDrop.py",
                 "GridEnterHandler.py", "GridHugeTable.py",
                 "GridLabelRenderer.py", "GridSimple.py",
                 "GridStdEdRend.py", "Grid_MegaExample.py",
                 "widgetTest.py",
                 "UltimateListIconDemo.py",  "UltimateListListDemo.py",  
                 "UltimateReportDemo.py",  "UltimateVirtualDemo.py", 
                 "Windows7Explorer_Contents.py",   
                 ]

# combine all the above
exclu = excluBase + excluDemos + excluProblems + excluSubDemos

for fol in captFolders:
    cFol = os.path.join(demoBaseFolder, fol)
    # folder to write capture
    scFol = os.path.join(captBaseFolder, fol)
    if not os.path.isdir(scFol):
        os.mkdir(scFol)
    # get .py files
    pyF = glob.glob(cFol + "//*.py")

    for item in pyF:
        path, filename = os.path.split(item)
        if not filename in exclu:
            pyFiles.append([item, scFol])

# following is useful for testing, e.g. if a particular file does
# not work correctly when capturing the screen define it below
# and un-comment the code to just run the screen capture for 
# the files defined in the list
#pyFiles = [
    #[r"D:\devTools\Phoenix\demo\BitmapButton.py", os.path.join(captBaseFolder, "")],
    #[r"D:\devTools\Phoenix\demo\Button.py", os.path.join(captBaseFolder, "")],
    #[r"D:\devTools\Phoenix\demo\CheckBox.py", os.path.join(captBaseFolder, "")],
    #[r"D:\devTools\Phoenix\demo\Choice.py", os.path.join(captBaseFolder, "")],
    #[r"D:\devTools\Phoenix\demo\agw\AquaButton.py", os.path.join(captBaseFolder, "agw")],
#]
totFiles = len(pyFiles)

# change to demo folder and add it to sys.path
os.chdir(demoBaseFolder)
sys.path.insert(0, os.path.abspath(demoBaseFolder))

def _displayHook(obj):
    if obj is not None:
        print(repr(obj))

class CaptureFrame(sc.SizedFrame):
    """The frame shown while the capture is done."""
    def __init__(self, parent, title):
        super(CaptureFrame, self).__init__(parent, -1, title, size=(640, 480),
                                           style=wx.DEFAULT_FRAME_STYLE)

        pane = self.GetContentsPane()
        self.fakeNb = sc.SizedPanel(pane)
        self.fakeNb.SetSizerProps(expand=True, proportion=1)
        self.fakeLog = wx.TextCtrl(self, -1)
        self.fakeLog.Hide()

        self.captFiles = 0
        self.nonCaptFiles = 0
        self.errorFiles = 0
        
        # some demos expect it
        self.CreateStatusBar()
        
    def runIt(self):
        self.doCapture()
        self.name = "Totals: "
        self.doLog("=====================================================")
        self.doLog("Error: %s, screen captured: %s, no capture method: %s" % (
                                                         self.errorFiles,
                                                         self.captFiles,
                                                         self.nonCaptFiles))
        self.doLog("=====================================================")
        
        # some stuff just doesn't want to close in doCapture
        print("TLW's before: %s" % wx.GetTopLevelWindows())
        for item in wx.GetTopLevelWindows():
            if not isinstance(item, CaptureFrame):
                try:
                    item.Destroy()
                except:
                    print("problem with Destroy")
                    print(item)
                    traceback.print_exc()
        wx.SafeYield()
        
        self.Close()
        
    def doLog(self, text):
        print("Name: %s: %s" % (self.name, text))

    def doCapture(self):
        # sort to get them in same order on Win and Lin
        pyFiles.sort()
        for item in pyFiles:
            path, filename = os.path.split(item[0])
            self.name, ext  = os.path.splitext(filename)

            apath = os.path.abspath(path)
            if not apath in sys.path:
                #self.doLog('path appended')
                sys.path.insert(0, apath)
            #self.doLog("\nTry to capture: %s" % self.name)
            try:
                demoModule = importlib.import_module(self.name)
            except ImportError:
                self.doLog("Import error: %s" % self.name)
                self.errorFiles += 1
                traceback.print_exc()
                continue

            scFileName = self.name.lower().replace(".py", "")
            if 'agw' in path:
                imgFileName = "lib.agw." + scFileName
            else:
                imgFileName = "lib." + scFileName
                
            if hasattr(demoModule, "runTest"):
                win = demoModule.runTest(self, self.fakeNb, self.fakeLog)
                
                # a window will be returned if the demo does not create
                # its own top-level window
                if win:
                    # so set the frame to a good size for showing stuff
                    frame.SetSize((640, 480))
                    win.SetFocus()
                    self.window = win
                    #ns['win'] = win
                    frect = frame.GetRect()
                    self.captureScreenshot(win, item[1], imgFileName)
                else:
                    # TODO: how do we capture those if they are already gone
                    #
                    # It was probably a dialog or something that is already
                    # gone, so we're done.
                    frame.Destroy()
                    return True
            else:
                self.nonCaptFiles += 1
                self.doLog("Module does not have 'runTest' method.")
                continue

            # old method with a 'runScreenCapture' method in each demo
            #if hasattr(module, "runScreenCapture"):
                #try:
                    #module.runScreenCapture(self,
                                            #self.fakeNb,
                                            #self.fakeLog,
                                            #self.captureScreenshot,
                                            #item[1],
                                            #scFileName)
                #except:
                    #self.errorFiles += 1
                    #self.doLog("An error occured")
                    #self.doLog(traceback.print_exc())
            #else:
                #self.nonCaptFiles += 1
                #self.doLog("Module does not have 'runScreenCapture' method.")
                #continue


    # TODO: review following, last three param not needed if we don't use runScreenCapture
    def captureScreenshot(self, window, imgpath, imgname, addwin=None, sleep=1,
                          wh=False):
        
        """Capture a demo screen shot
        
        :param `window`: window to capture
        :param `imgpath`: path for image
        :param `imgname`: name for image file
        :param `addwin`: additional window to close
        :param `sleep`: seconds to sleep before capture
        :param `wh`: a hack for e.g. FindReplaceDialog reporting wrong w/h
        
        """
        if isinstance(window, sc.SizedPanel):
            window.SetSizerProps(expand=True, proportion=1)
        elif hasattr(window, 'GetParent'):
            # e.g. PageSetupDialog doesn't have a GetParent
            if isinstance(window.GetParent(), sc.SizedPanel):
                window.SetSizerProps(expand=True, proportion=1)

        self.fakeNb.Layout()
        self.fakeNb.Update()
        window.Show()
        window.Update()
        window.Raise()
        wx.SafeYield()
        # sleep and additional update are needed to get rid of issues
        # see e.g. MaskedEditControls
        wx.Sleep(sleep)
        window.Update()

        # now do the actual capture stuff
        rect = window.GetRect()
        screenRect = window.GetScreenRect()
        #print screenRect
        #print window.GetSize()
        # FindReplaceDialog does not report correct size, so we hack it
        # until we find a correct solution
        if wh:
            swidth, sheight = rect.height+50, rect.width
        else:
            swidth, sheight = rect.width, rect.height
        # get the screen image
        capt_dc = wx.ScreenDC()

        # create a bitmap of the size of the screen to capture
        bitmap = wx.Bitmap(swidth, sheight)

        # create a memory DC and blit the screen capture into the bitmap
        memory_dc = wx.MemoryDC()
        memory_dc.SelectObject(bitmap)
        memory_dc.Blit(0, 0, # copy to coordinates
                       swidth, sheight, # copy this area
                       capt_dc, # from this dc
                       screenRect.x, screenRect.y) # copy from coordinates

        # select NullBitmap to release bitmap for use below
        memory_dc.SelectObject(wx.NullBitmap)

        # convert and write to file
        image = bitmap.ConvertToImage()
        
        if not os.path.isdir(imgpath):
            os.mkdir(imgpath)
        imgFullName = os.path.join(imgpath, imgname) + ".png"
        if os.path.exists(imgFullName):
            os.remove(imgFullName)
        status = image.SaveFile(imgFullName, wx.BITMAP_TYPE_PNG)

        self.captFiles += 1
        self.doLog("captured: %s - saved: %s - image ok: %s" % (imgname,
                                                           status,
                                                           image.IsOk()))

        if isinstance(window, wx.Dialog):
            wx.CallAfter(window.Destroy)
        else:
            window.Hide()
            wx.CallAfter(window.Destroy)
        if addwin:
            if isinstance(addwin, list):
                for it in addwin:
                    it.Hide()
                    it.Close()
            else:
                addwin.Hide()
                addwin.Close()
        wx.SafeYield()
        
class BaseApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init() # WIT

        # work around for Python stealing "_"
        sys.displayhook = _displayHook
        return True


# run it
app = BaseApp(False)
frame = CaptureFrame(None, "wxPython demo screen capture utility")
app.SetTopWindow(frame)
frame.Show()
frame.runIt()
app.MainLoop()
