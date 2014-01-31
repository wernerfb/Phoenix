#!/usr/bin/env python
#---------------------------------------------------------------------------- #
# Name:         TheDemoMain.py
# Purpose:      Demonstarting the widget/controls available in wxPython
#
# Author:       Based on EventsInStyle by Andrea Gavana
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 1999 by Total Control Software
# Licence:      wxWindows license
# Tags:         phoenix-port
#---------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
#
#
# TODO/Caveats List
#
# 1. Add methods/functions signatures and their Sphinx-based docstrings
#    maybe based on wx.html2 plus fetching the Sphinx docs in real-time.
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To any of the following:
#
# wxpython-users@googlegroups.com
# wxpython-dev@googlegroups.com
# andrea.gavana@gmail.com
# andrea.gavana@maerskoil.com
#
#
# End Of Comments
# --------------------------------------------------------------------------- #


"""
`TheDemoMain` is a small GUI which can be used to retrieve documentation about
events and widgets styles from the online SVN trunk wxPython Phoenix docs.


Description
===========

`TheDemoMain` is a small GUI which can be used to retrieve documentation about
events and widgets styles from the online SVN trunk wxPython Phoenix docs.

`TheDemoMain` requires a working internet connection with no firewalls
interferences: having that, just double click on a tree item and `TheDemo`
will download the appropriate docs for the item (window styles, events and widget
appearance as a screenshot on the 3 major platforms, if applicable).

It then saves the downloaded data in a cPickle-based file so that the next time
you need to look at the already downloaded documentation for a particular
widget/event you won't need to waste time to download it again. Obviously, over
time the saved docs become obsolete, so you can delete the saved data and freshly
download the updated documentation.


Supported Platforms
===================

`TheDemoMain` has been tested on the following platforms:

- Windows (verified on Windows XP/Vista/7);

"""
import os
import sys

import re
import HTMLParser

import wxversion
wxversion.select('3.0.1-msw-phoenix', True)
#wxversion.select('2.9.4')

import wx
print wx.VERSION

import wx.lib.six as six

import wx.lib.six as six
from wx.lib.six import exec_, BytesIO
from wx.lib.six.moves import cPickle
from wx.lib.six.moves import urllib

import wx.html2 as webview
import wx.lib.stattext

from wx.lib.embeddedimage import PyEmbeddedImage
from wx.lib.expando import ExpandoTextCtrl
from wx.lib.stattext import GenStaticText as StaticText
from wx.lib.scrolledpanel import ScrolledPanel

import wx.lib.agw.aui as aui
import wx.lib.agw.customtreectrl as CT
import wx.lib.agw.genericmessagedialog as GMD
import wx.lib.agw.pybusyinfo as PBI

wx.lib.stattext.BUFFERED = 1

import TheDemoCode as tdc

_importList = ['wx.adv', 'wx.dataview', 'wx.glcanvas', 'wx.grid', 'wx.html',
               'wx.html2', 'wx.richtext', 'wx.stc', 'wx.webkit', 'wx.xml', 'wx.xrc']

_styleHeaders = ["Style Name", "Value", "Description"]
_eventHeaders = ["Event Name", "Description"]
_platformNames = ["wxMSW", "wxGTK", "wxMAC"]

_baseURL = "http://wxpython.org/Phoenix/docs/html/%s.html"
_imagesURL = "http://wxpython.org/Phoenix/docs/html/%s"
_cssURL = "http://wxpython.org/Phoenix/docs/html/_static/css/%s"


_html_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

    <link rel="stylesheet" href="%s" type="text/css" />
    <link rel="stylesheet" href="%s" type="text/css" />

  </head>
  <body style="background-color:white">

  <br>
  %s

  </body>
</html>

"""

_css_files = ['basic', 'default', 'gallery', 'phoenix',
              'pygments', 'tables']
_hSpace, _vSpace = 10, 5


#---------------------------------------------------------------------------


def Import():

    modules = ['wx']

    for mod in _importList:
        try:
            module = __import__(mod)
            modules.append(mod)

        except ImportError:
            # webkit doesn't work on Windows
            continue

    return modules


def BuildWidgetsAndEvents(pname, windows, events):

    if pname == 'wx':
        module = wx
        stripped = '1Core'
    else:
        module = eval(pname)
        stripped = pname[3:].capitalize()

    for item in dir(module):

        if pname == 'wx':
            klass = eval('wx.%s' % item)
        else:
            klass = eval('wx.%s.%s' % (pname[3:], item))

        if 'Skip' in dir(klass):
            if stripped not in events:
                events[stripped] = []

            events[stripped].append(item)

        elif 'SetWindowStyle' in dir(klass):
            if stripped not in windows:
                windows[stripped] = []

            windows[stripped].append(item)

    return windows, events


modules = Import()
_widgets, _events = {}, {}
for pname in modules:
    _widgets, _events = BuildWidgetsAndEvents(pname, _widgets, _events)


#----------------------------------------------------------------------
# Some IDs for the menu

ID_EXPORT = wx.NewId()

#----------------------------------------------------------------------

__version__ = "1.2"
__author__ = "Andrea Gavana @ 03 Jun 2009, andrea.gavana@gmail.com"
__appname__ = "TheDemo"

#----------------------------------------------------------------------
about = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAztJ"
    "REFUOI2VU11oW3UcPfd/703uR3Jvkpt1/bBrM7sua+m2B20sWmaFIchQ+yD44EZBRPFJirAg"
    "rsEnmQ8+iGxWBYUOlCnFOJ1CEruxjtKta9fOJMQutU3aJGu3rPm8ufm6PiVMcA/+ns7D+R1+"
    "nHN+AIC52dk3QsHgF4VCYVTXdRP+xzAAkEokwuvRtbOKopxkWfbHq4HAZCyReHByPLMFmef3"
    "Cmzx3sqpwmMFbgeDYZTL8xQho/sP9Jxa3dh8VZMObb71obxtMjB2nq7u3Fq65uN44wXvp4Px"
    "RwWoBvjq/PlnZat1eiW00xKje+HoP4yedgmdCguHnSCd1ZCrkTm1Rt598aDxdmOPNMDQ8HBY"
    "VlrjC7FOXN+QELtfxnamBInTYREI+rsF7Gvjhnij4RNfSFeaAul0el82mx02m8X3IuvGvuvL"
    "VaTyVVwL7yKnlrF6T8WvyxlsZWugAFA0nqcMON70QCuV/Iwodhg5QQjFaGiERcceE4qVOp7u"
    "NWGgm8daSkMyXYHIA+vxEmuz8i4A3wMAc+GbbxXRZBKGR0YgKSJongUxsDi4l0dfpwCJJzjq"
    "EBBNlfGdL4HLvk0ce8EhNi6gB/r7ZlnWuGDgjHRnV8uTD+oSFdnRwIgiknkaFEXQZqGxW9Tx"
    "+U9x3N3IQLIx/tXAOT8A0HM3bsT9fwQWCE0vy2Zu1HVsyBzc1JDR6ijTHOoUAzvPwHcnj7lw"
    "Gk8dkvBa/26+3Zbz3rwZKjdTGB8fr7daxErqr3nUCFCtA7lCBZFkBT8vVbASq+C4qw1vjgiw"
    "1LZb29uPmJtFmpmZ4ZxO5/uKzdZ1338VJxws4qQbpj0SrDILopXRZS3iqC2LDkMJt+LxI6Re"
    "HwPwMQUAi4uLB2Sz9PsVf2B/QS3etdiVmSJlcmUr+kCxpFIshaqVZ+cdLVLI5Ro88Xd0re3y"
    "pV/u5DT1JQoAdF0nZ9wfvK6qxWdkuzI5MTERnJ6+OOjs7bsU+jPYkkoml/Law5fd7o+2IpHI"
    "cwLHvRMOhp3VWuWzf9Xa4/E0PfH5fLKqqvPTF3/Qz5x2f/ko0ePxMF6vt2dqauqJ/3qwBolE"
    "o1H31+cmf3t7bOyVx/H+AbSlT19ONLwLAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
appearanceBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAAK/INwWK6QAAABl0"
    "RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAGAUExURf6xOsVwHv+SAJpXJv/c"
    "C/68SP7Te6OC/+Lg3/7Vhv7CVjfW//rHs/6hJcC+vbZtJ+j7//317s6WX8ePU5Dr8/2gG7in"
    "nP/0tPyUFOnNtwD/Qf/fYf/wiP9iAP/vef7fp//Kfv/dkcqHQcSXbad3ANifYP/VMf/uhP/A"
    "MsrU2/62Sf+MF+CvXvSLCP/RSqyckfv28qZpR6GGctOSRduNLO3WxO+5h/uMMN+1g5R5ZuGd"
    "O8/6///8+OixX8J8xNZsAP/6+eKhRf62Da9gGNuBHP+uAwCJ//ZFAH9ILP/vnsvJyf6rNf76"
    "qP//otijcP7WtGefARm++fb29vWSKP64Qf+JSP/FAMV1If//96SVj/+HAMbv//69Ufzrz+Hf"
    "3phB6eOvasNqFKB3VN7e3v/rq/iAAMt+AP75//+Zff7/YrKUeaSCY8/r7/n////50f7LYp5i"
    "L9arev//S+vr6/6pTnRA/9WbXiH/NuCq/763speEhOK9nrmehf///+Hh4f7+/qmOZBQAAAB+"
    "dFJOU///////////////////////////////////////////////////////////////////"
    "////////////////////////////////////////////////////////////////////////"
    "////////////////////////////AMw+5nIAAADuSURBVHjaYqhFAwxAbFDtp1xo4SdUEwcR"
    "kCyLjc61rq93EBQWAwlUJ0TUuwW6aYb6Z9j46dcymBoLe3iLcAfmyTK5xwoqeTGo2tbWVvmK"
    "e6YoKir4O8gnMeiIMypZeXKysXFyKjhlqvEzOPr4yqjnc3HFsGqVhBWxMDJkWeXLcbGGMHh7"
    "84pqB0skMtTyZZtIszJ4izIxpeUIMDmDHFYZructKmrGGyAlFWAIEqitdNFgshOosC8vV4kE"
    "C9Rmi7rGs5fKRuky10EEOAp0JXjMmVKZ+WohArXJRgXOzsyWXvUwgdra4uTkuiAgDRBgALHg"
    "TCVj+ix+AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
clipboard = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAv9J"
    "REFUOI2tk0lvWwUURs/z7Pi5jsfEGeom6ZCWVA0WQUhpFCSgKEKlk0BCCuouLPkNlcoKCfED"
    "2LBBbLprhGjSUqQComohqWM7wYmTlCZ2bD8Pz+PzG8wiitV2zSd9u3uPzuJegVcjzNy+1n9p"
    "7u1ThUJBWfrup1R8I6GgIZCgIYDx2jwWgKQfN24GVsZPRB6eD940+4TLFoelfn4q+HP93JWG"
    "XTRbLE9Xlzs/bt0RQH8F8GS8Jyxe/+gr4613ZrWSx1Vp/O57VHxkldqyOxfYn/8+sCCcGBwm"
    "enJ5bjH5bZlV+d7LAPOXI+Zo7+yF27sTl/qNgTlx+viYORVfx5axMWN93/TFlZtCIDwmxHKG"
    "OCWm7PmV3fsxhVbXQC63FO/Gs/roxQO31JC4eOFNooPfoBs6LocIZjMioLnPmvL+09PzM8no"
    "D3dz97sGH7ZpH3NWJ3xT4+e22yHB5wvjczuw2Rx0BBNtHRoqONxO1rdLbrGWMEb3sku/1lAB"
    "TPEa0vPNxi9srtSDtgNykkwH0DugG6Doh3XarVjHpgVzaOSqebj31JGB6RYYm1n+kJPxot+W"
    "4SAvoelgHC1roOmg6hAYjFAemvGOeUyfdwEAoQaxtSeZx2EljpRJITc1mho0VVCNw7Z18PTa"
    "KUWuMzB55pOFMNEu4FPQ9zKdRT2TQjRSpA9aaB3QjMPqHegIIAgQOX2c1Z7LfR9EXdci4DAf"
    "qXwcUkuukP2zoXGP+DR7ltGRAIpu0GhrFMoq6Z06q39n2Fz9B6eWtbwRWvcey1UfWI4A/ybJ"
    "j+7Xl844s/Om9DL3lhSUagW1so/DyON3SbwXqDA03MLrapN4MOAPemRXFwC0KpL0sFJp3Jib"
    "TDv3yi9wBVsEemREZEy1CvX9IoXHsrGxU8vHYrU7i2vVdBdwC4yvf1P+HJlNrAx5q5OhZrVZ"
    "2S41/tqoSjvp9u7WczX1omKsaahbfTZ2akWkuzWawst3vQBW8aT93b5+08SzlLIXk4zdLY3t"
    "OhQB7fVP/F/yH85fZk5GyRuQAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
delete = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAgdJ"
    "REFUOI3Vk81vEkEYxp/Zme2yy7JA3SIaEhC/aJoUP649mXji4j/gwas3vfXUePTvqF5IvJmY"
    "phFtjAZN00j8iBqFauxu5EOE1gKzw4yXYiC0B48+c3kOz/Ob901mCI5QcX09KgM2rwJxUUi1"
    "oJQ8OeD8W7P2/c7y8s32KMfGSysrSruwtLEgBLkmubwKKeclSMwwdGaFQqi3ml1vr1sE8GIK"
    "UCwW6TBUusUH2m2pZFLTNGKaJty4g1TSBeccnVbjTbPpNcYvpSPj7+66UrK70Ng5Y8Ygjm3C"
    "jdlwwgYghxgKriCDxzTobaytrf1dQRuZn43G+beVzVN77ToMLYDiv0ElR8QywRgDo4xkM+kb"
    "hULhfrVaTU+t0Pa8rUuXlx7mzp6+fiaTwvtPn0EIEAQC/X4flDGEzDAMw6BxXcfUBL7v70ei"
    "8Z3Khyqell/DiswikUwhNusil8shv7iIwZDg0ZPyVjab/ToFAABIQKM6js0lYVoWKNVg2zZi"
    "0SgIIQAApaDGK5OAA6kJPzqH61DAv+g/AxAAhIAcCej193VCCMhE5CBICIQQ6HZ+6Rh7wXQs"
    "w5x4LBEKW3nHdhzHDmt22IRpzEBnFJ7vy9V7q/L5s5KIJ9xSw/fbwORvFB8rmw863c6X+s72"
    "lUw6kz9xPDFnmSaGImjVtmvvXr4qe3zQ81TP/jEq/QF/M8iAOpwAFwAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
down = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAj1J"
    "REFUOI19ks9LVFEUxz/3vTczTvPDRiZNLS0qIazFLKKkhSFCLaJdf0GbClpJhBFRmwhC2rpw"
    "1a9Nq4ogCYJ+k5ZgohVaOZhKYzMy08z4ft13W0zGOPPowPfCufd7PpxzOYKaOHU9tbejtetk"
    "Q7BBU0opDxBCidJaYe370pdbdy99Xq72G7WArcnt+3pSRy+HN8V06dlIz8XDYzW3ki8UMs+A"
    "/wN0PUgoGCYYCuJIEB5I5WIEDSBQa0eruwFQChT8PVBK4UnX1+oP+BcCANezcZXr14AfQG7I"
    "bGliueVK4tS7DYBj5wjt6DxwJNnUHgkFwofQDKFQmE6BopUFAZqmBeLRRN/FkeMdmWw6M1Ke"
    "es1VPAPgyUfk4P6W3sOpE+fj0YQWCOqi5OTIrqVxpYUQgkAoEk6leq6ZJdssT/4e4AIvAXQA"
    "0niN3T8n2pM797S1dHZLYYpseZ68uYjtlXA9E6lMIZSmFhbTw+8nHtyYG6vMqq/PMvvKMqO7"
    "Mx8a400HY/HYtkxplpKzgiMrAIMQv5Zyj8fGRwceDhUL63V61X8w9Ty32p5yZyLRaJ+j5xJF"
    "O4MlC+gigLUqJqdnpk/fuTKXrq7ZAAAYH134saunYTkWifa7ej4sPRtRji+nvy6dHR4Ye1fr"
    "rwMAvH307VOqv81LNG7pNVTMysznBofOvLjv5/UDCADNyE8mm5ubiznrzb3bT2/m08j1tzoz"
    "lYUK1Ehr7Qputm1Udt4uUNkwp0ouIKuJmo+qw/MRfwCOVvmSKk0KggAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
eventsBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAr5J"
    "REFUOI2NkFtIUwEcxr9z5k5znl11U6d0sXnZ0bQUxVsqeClLgwp76KlSH5JuCIFBdBF6qAch"
    "CqGXegmxSCxvWSqp88LUxKVOp860pu6ibqGb13Z6kkSc9b384Q+/Hx8fB39DZmZmHpycnLRX"
    "va2qGNWPGuVyuZOmaaHNZnPgX6FpWtbXp519XVnT296hdX1u6hjX6cZN2dk5xXtxHAAoKLia"
    "X1hYdMuxTsVJpb4KitpHcCm+lOTwaKm3WJSUkBXZ3FzXDWBtp4AEAJ1OJwxWxZ/nciiAJTA2"
    "ZvhtsSywJtMCQkLi4y1WaxKApd0akAC8U9JOxBmNJvC9RKj9UD2cfykn/Mnj0pcbmwSGhvQQ"
    "SwJ8GSY6bVeBQCBQ0iK/3I1NFmCBA/sVKwD0qtCgGb4nD160J1iCE+h0OmPdDsEwMdeqa7Rs"
    "yxcdqxuxshMTVqteb17XaAxsY7OOPZtX1O6OJQHAkxapPja8m+d4EBCL+PAgKR8+n+b6yLzR"
    "0tJosy/O8wH4lJe/yADAYxiG2hIQW5fL5R69UVzWezhIQaiYMNJiMrtGxqbJ509Li09mJHml"
    "pJ/KjDpyLGbqp6F/dHhg4v69u1d2thELBNLLACLiEnN7/ANDywCklZQ8bKqpb5+xLqyyDqeL"
    "dThd7IDWsHT95p1nAChym8C+tLT4CsBQT1fthTmj/hGA1pWVdZsqLEqhVmtWzuVd7Kyta13j"
    "cIW0ze7wA7Dh4WabKQCQyfyTmciE3OkfZgx+Gxz+VF+ZmpyYqnWxvHClMiJLKlekuxMAAKzW"
    "ua6uLnWfUChPPqQMj656r/5ut68GLDtXoenp7F60zLZx9hIAIObnTb4CgUSpDFFJlpdXRRSP"
    "Rwxqe82NDW8qnI5fPcQ/BAAAhSLotkgiCU46fvpM/9e2zrlZ4+DcjOHB/7A74hELgN7++QML"
    "xRPotiKh8gAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
exit = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAyFJ"
    "REFUOI09k01oXGUUhp/vO9+dezM/yUzSSZMa60+JKTSzqEkXtQi1WVSwlULRVYUsuyiC0KVV"
    "cB2KKwVF6UrEgGSRRaQLmyxKKdK0mybEBM3PaGLMZO78ZX7u/T4XUzxwOPCuzvvyPgpg7ubN"
    "seHx8Q+TuVxeG4N4HtoYtAjqxdVagwgA9f39tfWHD398/+7df81XU1Ov9508+a0EwdtRu41Y"
    "C3EMIjilEGPAGJwIWgRESPf3x69NThY+Hx7+xHRarfc61epbjTjGiGC0xoggvk9voYANQ9o7"
    "O90vRFAiKM8TyuVr2bGx780/GxsDr46Oip/P45TCaU0MBPk8L01McLS5ye7KCmiNGIN6YbG5"
    "uhrsPXnSp9uVCp2DA1ylgg1DTG8v2clJRCmUtag4JnX6NOnz51FxjCmXMYeH2JUVqFTQRBE2"
    "DLGHhyR6exm9cYNXLl3CNwZnLarTIR0EDF24QPbyZSSK0MvL8OgRAmhjLa5ex9XrnJiaIjU4"
    "yF/37tF8/hwFqFaL6uws9YUFMoUCfj5PvPQAz3Uz08ZaqNXwjGGgUKD27BnlhQVssUhtcZHm"
    "48eovT2ac3O4Ugl/9BQ6ECSXxvgGkwRUrYbEMSaZpLa9jd3fxxnDwcwMnlJ4jQbRn38QF4uY"
    "wUFkIIsc1ZFqA5O0Fl2v0ykWiUol/JERdBRBGOKiCFetEldCVGEcPTRE/PQ3lIAEPhiDTjqH"
    "ajQ4Wltjf36ezNmzZK9cIdrdJd7cxJVKkD9G6vZtJJej/et9lHJ4QQIjdC3oVgvbarEzM0Pf"
    "mTO8fOcOmXPnaC0tYXp6SF+9SjAxQXP2B9oP7qMTCYyCFAaTMsZJHKOdo7W1xfr0NCO3bpG7"
    "do3sxYtgLXZrk9oXn9Ga/xlFDJkkohUJY5z6aWDgo2POfd0pl1O+tfhAoDWpfJ7k8eN4zuLC"
    "EqrTRGeS6HQP0pfhb2T9u+Xfr6t3IT/9xqlPh/zgA9/aHtHKeYAXWzxru2UJfFTCQycE53sq"
    "RB0sFne//Hh14xsFMAL975wYfDPpB1m6xHYnpkvm/9uVtqvV4i/N5lPg6D8+CEt0sLUujQAA"
    "AABJRU5ErkJggg==")

#----------------------------------------------------------------------
extraBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAvpJ"
    "REFUOI2lk19MlXUcxj+/933PezwvdF4OCBxg5g4cp9IQDHQsxWq6YsNlUW7pNKYXtLm5vGhz"
    "y7zLorpwja0CabU2HVt1YUuT/jAxU0eaOEUMEUqSIxzOOXA4vH/Ov7c7Jce66bl7novPvnv2"
    "fOF/Sjwa7Fu39HBFQeagLDs5yYxD3BbG6Kzr6Infw28vBpAXmtZa38GqUucd7TGhKm6BJAvA"
    "cQnSDQXeXOn2lHn2UYC00Kz1Z9s0TYhYPEN0LkPCgqykosiK8LlSBxa74F+AmbkMJU/vY+f+"
    "Qzz70l5C8woRS8FQ8tA8suej/Y3u/+ygc/fyyO4Pf8hP3uklYZhMR2fx5mrolVvoadser2vM"
    "b80YwW45t4r56T6w7rUoCwFmVhsy717ZkHYvxZeTxldYSiItQ3QYfZkaydU3d3sqGtADa5kZ"
    "W8lQT9cHD0us7XDdSSzZ9Hj4m+qamipQvQhJQXUsrvzURk1Ts+4rqxdzE7eQkwaat5jZyT8V"
    "ARBsPO2OEdvrofjjM531DHbsxMEBIN83T13jBvTy57FD3ZgRwdQfBknTjlh24ikZHJEKDOzS"
    "1WXHejrXc1VoXF6xg5HyHWRLSnihxkYPbsWa6ERSDaCI1Mi1SdOwnqt74/Sgsrr5i21lUvjz"
    "199s5lxEZtBwSFngv/8te4IX0YMvYt37BMmVJhkPMP7zb3x2Y9WnR491DABIxyvf//pES5TJ"
    "m99zaQKMmKDw71O87LtA0RNNJO93IasOdnw5ob7LFAWq2a73vfVgB5IQkuLWOH9pmqBi4Bvp"
    "5tWCi2SdUkLX28liMR8t4+4vtzhydRsuzYssS8pDwIoth8Z6v0wvSYbSJ4/3s97sonJjK+7x"
    "8wyf/JWBnij9Z65xoLeJPGfcGD33le2p3HzkAWDNa+3vafWb8v1+/FMziY6h21MkB78jUN1A"
    "Ts5KxvqHeffsM7G/UkU/qi41oD1ZV7impf3woksEeGVjnllbUaysW12O47Iv2OHwnq1t10cX"
    "+wOAfwAJ9yQGhieeeAAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
question = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAltJ"
    "REFUOI2Vk19IU2EYxp/jGsy8KVBGsIsVpAzK1Gh2VSJ0ZTelCXPGCHNG0IWywIv+OC/6R4YI"
    "gTpqabZlLLtQMrCrLVo6hzoImrGG1TRiOxvs7BzPct/bhbpUJuYD3933e77v4XlfDjlFXGWL"
    "4xGAixy4gU99BgvAUe67uWHbfee0lF7JUOfgpFjZ4rABxP03/ODltBRPytQ7HqRESqbOge1N"
    "9myGnf111SWNl2uOqHrGgliMpbDEi2itLcsnwEhwYqqPzBvjKDbCtdXFjc01R1WP387jFy+B"
    "GCGRSiMQ5tFWW6qMCbJOVHu0Eb9rDLBuybz27c7hAF3tnaR1+eajZOpyU/tTH8UFmTqeeUW9"
    "eSgbR3HySknXuarDTeazpaqe0S9Y4iUwIoxO/sD01xiMVYfw5uMCEoKM2VAU1+srlLGkrBPV"
    "7n2L/pGJPEa4ZKk/rhr2hPEzKiCTYauHMViNZbj3ag6MERgRFn4LGJgIor3hRD6AJgDI4whP"
    "7gz5JMOpgziwPx8rmUzWxNTlxufvCTDGwBiDpnAvTGeKcdfhkziO7ACgiPhd70W1W8sLaV3r"
    "+VJlIMwjkUqDGGHQchqvPWFkGIOmsAA3GyrQ7ZqR3nlDL6b6jdcAKxSAFRG/a0xUu7UxQda1"
    "1R1Tzn2LIiGk4foQBmMETVEBbhjK0e2akcZX4WyVazWum3i0fFLWWS6UK2dDMcSTMjRF/17e"
    "CuecRL3ZYeuwe8V4cpm6RwIUTy7TLfvm6nYcZ715yHbb7hXF5T87wts4Eqdvdj4Ex0xEeO6z"
    "Gdt2sY2701++vnGp+mtp3wAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
stylesBmp = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAp5J"
    "REFUOI2Fkl1IU2EYx39nbs5jm23h0X3YqtmNZGUl1SiiMsigSy+CiigxSiGKgjIIiqIQvIlV"
    "CEUXaYEXBUEfUEkEQZJoGqsuRO3DNFLnjno22c45bxdLnQX1wAPPy/Pw+7/PB/xhH6vlix/q"
    "i+8B+YD9z/x/7WvjqsfJ3mbRuMN+FSiuX45yq4SKY8soBKyA9G9AU+iNOfFAJDsOiYHba0bG"
    "Hm4TYzcXTVS42A0UAFmZ9daZ4NUutvs3eU941ng3or3F6rWzpKAkn5/tNIRj79ti+AEXEP0L"
    "0LOHOyvrK/fj9oMxAVo3GJMQi9D1RE3Uv6AfSACTgJEJyAJoitDm7e3zuvX+MnfRKKQGwfgC"
    "timchdjutvJO1WkD+gD9rx+cCi044yuyVOmOUkYir1HWAzlpdyyFy6cJ7btAy4zg0daYmAFI"
    "Vypye3Zu9a7qixfGrz+L5547O8C2SpUrRxbxqMfD5nKN0sJJ2sv6Z1XrtjhnY+np+ZDoHFK4"
    "0a6zrnwddetb+DaUQ1PHJvL9y8lTijD0FLLDhae4jIMVAbSkACFAkpDWFuTsBdgQ/tEyPdiF"
    "on+mdyy96oJlpTjdHkwz3bY9N48DIRe6mTGD5pedToBrEXAHVpM0VtBYNUV2djaKomC3p4/x"
    "+H2NuA6LXRYiw78XIYElGAzagsGgDWDKdKCRRyAQwOfzUVtbO6sUTQiiCYEpIDZtoE6bxBIm"
    "FlmWw7IshwFiWgo1bmC1WqmpqQGguroaADVuosZNvoybRDXBmGYQ1Yy5SwSYTqV7/dg7zMkz"
    "lwBI6ibdn76jmw4ABkZ1RicNhCQhIeYDxrU04PAjK5JkQZIkEBIIE6c8VzcyNTfFeQBVHc94"
    "pRUEkLfQxUQiBUDD8xQr/bY0GMEv7ZkCqPx/e6IAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
mondrian = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAHFJ"
    "REFUWIXt1jsKgDAQRdF7xY25cpcWC60kioI6Fm/ahHBCMh+BRmGMnAgEWnvPpzK8dvrFCCCA"
    "coD8og4c5Lr6WB3Q3l1TBwLYPuF3YS1gn1HphgEEEABcKERrGy0E3B0HFJg7C1N/f/kTBBBA"
    "+Vi+AMkgFEvBPD17AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
unknown = PyEmbeddedImage(
    "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")

#----------------------------------------------------------------------

error = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0"
    "RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAQQSURBVHjaAEEAvv8BXTIyAAL9"
    "/UEy6Oip+fn5BqAAAHX1/f2bBP7+ACMDAwA4BQUAB/z8AAH6+hQhCQm7FAsLKpPm5qfh/f1g"
    "4QAAAAIAQQC+/wMtGBhBLufnr1w5ORI1JycI+traR9QBAev4/v7NFQICABsDAwAB/PwUFwAA"
    "vDdJSTA0X18DIujoL9Lm5iLZAACyAgBBAL7/A2ADA8xhKSkREoaGAAQ9PQAm398DAeDgRtP/"
    "/+gKAgLOHQEBDBr//782NDQwIGpqAP84OAAgFBQBKOXlLr3n5wcCAEEAvv8E9fn5CAcBAQD5"
    "3NwA+A8PAA5aWgBY+PgG/cjIlMcCAhUUAQFSMScnMB1VVQD/AAAA99HRAAj4+AAFBQUBAf//"
    "NAKI+TEf36uvT5546N+4wczMxcXwE2gYu6Qkg8T79yxCb986KUtKSiu7ujKwAA3/9ewZA/fN"
    "mwxX1q5lyD979sXZ//9LAAKImZeL69w5oJ//v37tqvP4MQsj0IA/wEBjBWrg+fmTUVRZmYGD"
    "lxesmePpU4Zbx44xFF269OLQ379xQAftBgggZgFOToYvf/+ePcPA8ILl0yc35RcvWP79+sXA"
    "9PMnAxc3NwML0LA/L14w/H79muHarVsM5TduvDj6928UUPNeIGYACCBmbXFxBkFgVPEwM597"
    "xcn5W/DXLxexp08Zf338yPDn/XuGX0CNPz5/ZvgGNLD93r13R37/DhBkYDjMA9QMChOAAGLR"
    "FBEBpQOG/3/+8Mn+/Bmi8OkT40eg5ncfPjB8BXqHhZ2dgRvoHVFRUQYvMTHuN48fa/xgYDjG"
    "C9R8H4gBAohZDxhgP///55H68eOg34sXxmJAze+BEh/+/2f4DqT/sLAwsAK9ycbGxmAhJcUi"
    "yczscfrDh9dAQ85+BcoDBBCztoyMpMz37/vCnjwxkAY69QNQ8BsQswI18EtIMHACaRBgBbqE"
    "CYiNZGRYRP//d738/v3rF0BDAAKI2U9A4EjMw4f6il+/MnwEKvwJxCBNT4SFGab/+PGem42N"
    "WY+bm/kvMFWyAMWZga4xVVBgkfj3z23f27cPAQKISebzZ21toOa/QI3/gJgfGKCPgZq7v317"
    "sfPdO7+Fr19nnv/585cIUCMTKMEBY4UFmF7M5eTYBJmZkwACiPk1F5cCPyengTYwzlmBtpwG"
    "aq7//v3F+Y8fo9gYGQ+xMzCcv/7ly0sxFhY3HSEhFkFgmvgEjJ2ms2d/7Pz6dSpAADHIAkNX"
    "R1x80SoxsX+bxMX/6/HzPwc6xBnkbw6gjWpAF6kDaUNGxoxFSko/7lpY/E/n5//ByMBQAlID"
    "EEAMqmJiDNJAWxX4+dsluLh2A8XcGKAAZoA+MEdqAvn6jIwx+iwse5kZGAphagACDAAeLHBa"
    "S9SUbwAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------

method = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAAXNSR0IArs4c6QAAAARnQU1B"
    "AACxjwv8YQUAAAMAUExURQAAABpDcThcfAA+nQZAiglFiwBGmQBFnQNNmAJOmgpOnxVFgx9N"
    "ixBUgxZTjBNRnhVZlgBLpQBOrwNQogBQsQBUsgBWuwBcuRdmnwBirgxlpwJhvQx3ux1gphtu"
    "pBpnuR9stBt0thl3tR11vCZSkyNbljZVizBenClijSJqpChvpytrqSZxqz1noTFwpTJ7sgBd"
    "xAJkxQFnyQ5ryg5tyQFv0ABxxAR1wQ13ww552RtywRl6yRh/zBF32yN6wSF50EBrjk1rj0dy"
    "lUhrpVF7tzqBrzaFvh+FzxCD1haH1xGJ3xOM3RuE3wGF5wqH4Q+L4xuP4h2L4h6S6R+V7BGT"
    "8SaDxiOEyS6M0iCP6SiO4Cma5jCa5jWZ7zuW5TSj/Dqp+zuu/0CKuVyHvlSTvEKDw0OZykaT"
    "21+KwVaRyVCZxlqWzFifzUCX5ESV5Fmk3V2i2UOo8E+x/FKu91W5/1qz/32Rw3Wq1Hq03GC0"
    "+nqv43S76Xu452DK/2rB/27E/23L/3HC/37N9nfR/33V/46p1Iut2oezzp+vyJiq0pS834q0"
    "5oLH/4TW/5rA5JTL8pzn/5v2/6TG367G8qzK8KvQ66PR8qvw/6r2/6v//7nl/7rm/7Lw/7f7"
    "/7f//7j5/77//8P0/8L2/8b//8vw/832/8r//876/97m/93v/9H3/9L+/9X//9r//93//+n/"
    "/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsM92YAAAEAdFJOU///////////////////"
    "////////////////////////////////////////////////////////////////////////"
    "////////////////////////////////////////////////////////////////////////"
    "////////////////////////////////////////////////////////////////////////"
    "////////////////////////////////////////////////////////////////////////"
    "/////////////////////////////////wBT9wclAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAA"
    "GXRFWHRTb2Z0d2FyZQBQYWludC5ORVQgdjMuNS44NzuAXQAAAOxJREFUKFNj+I8GGMD8dWtX"
    "LV06fw2ICRJYMbkrS18utXH2YpDA2rayjJS02EhPcxklncpJ/xlWJzc01ZXEBAZ7R0VbK+gC"
    "BVyLa2p7musLC8Ikfex5gAKJ8QkV07q1NPun21maqP9nWJMZEJS3eqaTw6wFAuLSLkAV2V7+"
    "bgtXdfauXKJtJJr+n2FZlZ9v+KL8ebNVF3EYGCYB3VFuFmIzoSgnl3OOvBh7K1BgoqKHxYwI"
    "UyHjuWyCsu0gl1ZLhbrHidgyc7GwMkKc3scroWwlzK+i1gL1y/+pGnp83M6lYH9CfDuFybFj"
    "OSQcAEA5icO2ytz2AAAAAElFTkSuQmCC")

#----------------------------------------------------------------------


def BuildDictionaries():
    """
    Dynamically builds two dictionaries of widgets/events depending on which
    modules are available (or can be imported) in wxPython.
    """

    modules = sorted(_importList)
    widgetsDict, eventsDict = {}, {}

    for mod in modules:
        attach = ""
        try:

            if mod == "wx":
                module = __import__(mod)
            else:
                module = __import__(mod, globals(), locals(), fromlist=mod[3:])
                attach = "%s" % mod[3:]

        except ImportError:
            continue

        name = _importList[mod]
        widgetsDict[name] = []
        eventsDict[name] = []

        for item in dir(module):
            if attach:
                to_eval = "wx.%s.%s" % (attach, item)
            else:
                to_eval = "wx.%s" % item

            try:
                if issubclass(eval(to_eval), wx.EvtHandler):
                    widgetsDict[name].append(item)
                elif issubclass(eval(to_eval), wx.Event):
                    eventsDict[name].append(item)
            except (TypeError, NameError):
                continue

    return widgetsDict, eventsDict


def ReplaceCapitals(string):
    """
    Replaces the capital letter in a string with an underscore plus the
    corresponding lowercase character.

    :param `string`: the string to be analyzed.
    """

    newString = ""
    for char in string:
        if char.isupper():
            newString += "_%s" % char.lower()
        else:
            newString += char

    return newString


def ReadStyleDocs(frame, selectedClass):
    """
    Starts the reading process of the online wxPython Phoenix documentation.

    :param `frame`: the main application frame;
    :param `selectedClass`: the class for which we seek the docs.
    """

    img = mondrian.GetBitmap().ConvertToImage().Scale(16, 16)
    busy = PBI.PyBusyInfo("Connecting to the wxPython website...", parent=frame,
                          title="The demo is busy", icon=img.ConvertToBitmap())

    try:
        url = _baseURL % selectedClass
        fid = urllib.request.urlopen(url)

        originalText = unicode(fid.read(), "utf-8")
        text = RemoveHTMLTags(originalText).split("\n")
        eis_class = FindWindowStyles(selectedClass, text, originalText)

        splitted = originalText.split('\n')
        to_read = False

        for index, line in enumerate(splitted):
            if '<dl class="method"' in line:
                to_read = True
                next_line = splitted[index + 1]
                method_name = next_line.strip().split('.')[-1][:-2]
                method_description = line
            elif line.startswith('</dd></dl>'):
                to_read = False
                eis_class.AddMethod(method_name, method_description)
                continue
            elif to_read:
                method_description += line

        frame.LoadData(eis_class, selectedClass)

    except urllib.error.HTTPError, e:

        if e.code == 404:
            # URL not found
            frame.LoadData("Documentation not found for class %s" % selectedClass)
        else:
            # Some other urllib2 error...
            frame.LoadData(None)

    except urllib.error.URLError:
            frame.LoadData("Documentation not found for class %s" % selectedClass)

##    except IOError:
##        # Unable to get to the internet
##        frame.LoadData(None)
##
##    except Exception:
##        # Some other strange error...
##        frame.LoadData(None)

    del busy


def RemoveHTMLTags(data):
    """
    Removes all the HTML tags from a string.

    :param `data`: the string to be analyzed.
    """

    p = re.compile(r"<[^<]*?>")
    strs = p.sub("", data)
    strs = strs.replace('  ', ' ')
    h = HTMLParser.HTMLParser()
    return h.unescape(strs)


def FormatDescription(description):
    """
    Formats a wxPython Phoenix description in a more wxPython-based way.

    :param `description`: the string description to be formatted.
    """

    description = description.replace("wx", "wx.")
    description = description.replace("EVT_COMMAND", "wxEVT_COMMAND")
    description = description.replace("wx.Widgets", "wxWidgets")
    description = description.replace('&#8217;', "'").replace('&#8221', '"')

    return description


def FindWindowStyles(selectedClass, text, originalText):
    """
    Finds the windows styles and events in the input text.

    :param `selectedClass`: the class for which we seek the docs;
    :param `text`: the wxPython Phoenix docs for a particular widget/event, stripped
     of all HTML tags;
    :param `originalText`: the wxPython Phoenix docs for a particular widget/event, with
     all HTML tags.
    """

    winStyles, winEvents, winExtra, winAppearance = {}, {}, {}, {}
    inStyle = inExtra = inEvent = False
    inStyleSpace = 0
    inEventSpace = 0
    inExtraSpace = 0
    imagesDone = False

    eis_class = PhoenixClass(selectedClass)

    for line in text:
        if "following styles:" in line:
            inStyle = True
            continue

        elif "Handlers bound for the following event" in line:
            inEvent = True
            continue

        if "following extra styles:" in line:
            inExtra = True
            continue

        if "Control Appearance" in line and not imagesDone:
            winAppearance = FindImages(originalText)
            continue

        elif not line.strip():
            if inStyle:
                inStyleSpace += 1
                if inStyleSpace >= 2:
                    inStyle = False
            if inEvent:
                inEventSpace += 1
                if inEventSpace >= 2:
                    inEvent = False
            if inExtra:
                inExtraSpace += 1
                if inExtraSpace >= 2:
                    inExtra = False
            continue

        if inStyle:
            if ':' not in line:
                inStyle = False
                continue
            start = line.index(':')
            windowStyle = line[0:start]
            styleDescription = line[start + 1:]
            winStyles[windowStyle] = styleDescription
        elif inEvent:
            start = line.index(':')
            eventName = line[0:start]
            eventDescription = line[start + 1:]
            winEvents[eventName] = eventDescription
        elif inExtra:
            start = line.index(':')
            styleName = line[0:start]
            styleDescription = line[start + 1:]
            winExtra[styleName] = styleDescription

    eis_class.SetProperties(winStyles, winExtra, winEvents, winAppearance)
    return eis_class


def FindImages(text):
    """
    When the wxPython Phoenix docs contain athe control appearance (a screenshot of the
    control), this method will try and download the images.

    :param `text`: the wxPython Phoenix docs for a particular widget/event, with
     all HTML tags.
    """

    winAppearance = {}
    start = text.find('id="appearance-control-appearance"')

    if start < 0:
        return winAppearance

    end = start + text.find('div class="line-block"')
    text = text[start:end]
    split = text.split()
    plat = None

    for indx, items in enumerate(split):

        if "src=" in items and plat is not None:
            possibleImage = items.replace("src=", "").strip()
            possibleImage = possibleImage.replace("'", "").replace('"', '')
            possibleImage = _imagesURL % possibleImage

            try:
                f = urllib.request.urlopen(possibleImage)
                im = f.read()
            except urllib.error.HTTPError, IOError:
                im = None

            winAppearance[plat] = im
            if 'GTK' in plat:
                break

        elif 'alt="wx' in items:
            plat = items.replace("alt=", "").replace("'", "").replace('"', '').strip()

    return winAppearance


class PhoenixClass(object):

    def __init__(self, name):

        self.name = name
        self.methods = []

    def SetProperties(self, *args):

        self.winStyles, self.winExtra, self.winEvents, self.winAppearance = args

    def Any(self):

        for item in dir(self):
            if item.startswith('win'):
                item = eval('self.%s' % item)
                if item:
                    return True

        return False

    def AddMethod(self, name, description):

        for mn, md in self.methods:
            if name == mn:
                return

        self.methods.append((name, description))

    def GetMethods(self):

        return self.methods


class MyExpandoTextCtrl(ExpandoTextCtrl):
    """ Adds self-adjustment on size events to `ExpandoTextCtrl`. """

    def __init__(self, *args, **kw):
        """ Default class constructor. See `wx.lib.expando.ExpandoTextCtrl` for more information. """

        ExpandoTextCtrl.__init__(self, *args, **kw)
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for `MyExpandoTextCtrl`.

        :param `event`: a `wx.SizeEvent`.
        """

        self._adjustCtrl()
        event.Skip()


class EmptyPage(wx.Panel):
    """
    A simple notebook page which gets displayed when no documentation is available
    for a specific widget or there is no internet connection.
    """

    def __init__(self, parent, message):
        """
        Default class constructor.

        :param `parent`: parent window. Should not be ``None``;
        :param `message`: the error message to display.
        """

        wx.Panel.__init__(self, parent)

        static = wx.StaticText(self, -1, message)
        stBmp = wx.StaticBitmap(self, -1, unknown.GetBitmap())

        boldFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
        static.SetFont(boldFont)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 50))
        sizer.Add(static, 0, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add((0, 50))
        sizer.Add(stBmp, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(sizer)
        sizer.Layout()


class NotebookPage(ScrolledPanel):
    """ A simple notebook page which holds window styles and events information. """

    def __init__(self, parent, data, num, parentName=None):
        """
        Default class constructor.

        :param `parent`: parent window. Should not be ``None``;
        :param `data`: the formatted docs to display;
        :param `num`: whether to display 2 or 3 columns of data;
        :param `parentName`: if not ``None``, one of the wxPython sub-modules
         (`wx.grid`, `wx.animate`, etc...).
        """

        ScrolledPanel.__init__(self, parent, size=(0, 0))

        self.SetBackgroundColour(wx.WHITE)
        self.defaultb = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)

        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            if 'phoenix' in wx.PlatformInfo:
                self.colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT)
            else:
                self.colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DLIGHT)
        else:
            self.colour = wx.Colour(237, 243, 254)

        self.colWidths = []
        self.dirty = True

        self.SetData(data, num, parentName)

    def OnMenu(self, event):

        print('OnMenu')
        evtObj = event.GetEventObject()
        ID_CLIPBOARD = event.GetId()
        menu = wx.Menu()
        mi = wx.MenuItem(menu, ID_CLIPBOARD, 'Copy to clipboard')
        menu.Append(mi)
        menu.Bind(wx.EVT_MENU, self.OnCopyToClipboard, id=ID_CLIPBOARD)
        self.PopupMenu(menu)
        menu.Destroy()
        print('OnMenu')

    def OnCopyEventToClipboard(self, event):

        evt = event.GetEventObject().GetLabel().replace('(id,  func)', '').replace('(id,  fn)', '')
        if 'EVT_AUI_' in evt or 'EVT_AUINOTEBOOK_' in evt:
            pre = 'aui.'
        elif 'EVT_STC_' in evt:
            pre = 'stc.'
        elif 'EVT_CALENDAR_' in evt:
            pre = 'cal.'
        elif 'EVT_HTML_' in evt:
            pre = 'html.'
        elif 'EVT_WIZARD_' in evt:
            pre = 'wiz.'
        else:
            pre = 'wx.'
        newtext = 'self.Bind(' + pre + evt + ', func, id=ID_MYWIDGETID)'
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(u'%s' % newtext))
            wx.TheClipboard.Close()
        print('OnCopyToClipboard')

    def SetData(self, data, num, parentName):
        """
        Actually sets the data to be displayed.

        :param `data`: the formatted docs to display;
        :param `num`: whether to display 2 or 3 columns of data;
        :param `parentName`: if not ``None``, one of the wxPython sub-modules
         (`wx.grid`, `wx.animate`, etc...).
        """

        names = data.keys()
        names.sort()
        boldFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
        italicFont = wx.Font(boldFont.GetPointSize(), wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)

        xpStyle = wx.TE_READONLY | wx.NO_BORDER
        missingTooltip = "This style may only be available in wxPython trunk\n" \
                         "and not in your installed wxPython version."
        integerTooltip = "Hex Value = %s\nInteger Value = %d"

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.GridBagSizer(10, 10)
        sizer.SetEmptyCellSize(wx.Size(0, 0))
        backColour = self.GetBackgroundColour()

        if num == 3:
            headers = _styleHeaders
        else:
            headers = _eventHeaders

        lenh = len(headers)
        for i, head in enumerate(headers):
            st = StaticText(self, -1, head)
            st.SetFont(boldFont)
            sizer.Add(st, (0, i), (1, 1), wx.EXPAND | wx.BOTTOM, 5)
            st.SetBackgroundColour(backColour)

        for j, name in enumerate(names):
            description = data[name].strip()
            tooltip = ""
            if parentName != "Core":
                pythonValue = "wx.%s.%s" % (parentName.lower(), name)
            else:
                pythonValue = "wx.%s" % name

            if num == 2:
                st1 = StaticText(self, -1, pythonValue)
                st1.SetFont(italicFont)
                st1.Bind(wx.EVT_RIGHT_UP, self.OnCopyEventToClipboard)
                sizer.Add(st1, (j + 1, 0), (1, 1), wx.EXPAND)
            else:
                colour = wx.BLUE
                try:
                    val = eval(pythonValue)
                    value = "%s" % hex(val)
                    tooltip = integerTooltip % (value, val)
                except AttributeError:
                    try:
                        pythonValue2 = name.replace("wx", "wx.")
                        val = eval(pythonValue2)
                        value = "%s" % hex(val)
                        pythonValue = pythonValue2
                        tooltip = integerTooltip % (value, val)
                    except (AttributeError, NameError):
                        value = "Unavailable"
                        colour = wx.RED
                        tooltip = missingTooltip

                st1 = StaticText(self, -1, pythonValue)
                st1.SetFont(italicFont)
                sizer.Add(st1, (j + 1, 0), (1, 1), wx.EXPAND)
                st2 = StaticText(self, -1, value)
                st2.SetForegroundColour(colour)
                st2.SetToolTip(tooltip)
                sizer.Add(st2, (j + 1, 1), (1, 1), wx.EXPAND)
                st2.SetBackgroundColour(backColour)

            st3 = MyExpandoTextCtrl(self, -1, FormatDescription(description),
                                    style=xpStyle)

            sizer.Add(st3, (j + 1, num - 1), (1, 1), wx.EXPAND)

            for static in [st1, st3]:
                static.SetBackgroundColour(backColour)

        print sizer.GetCols()
        sizer.AddGrowableCol(num - 1)
        self.columns = num
        self.rows = len(names) + 1

        mainSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(mainSizer)
        mainSizer.Layout()

        self.flexSizer = sizer
        self.SetupScrolling(scroll_x=False, scroll_y=True)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for `NotebookPage`.

        :param `event`: a `wx.SizeEvent`.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for `NotebookPage`.

        :param `event`: a `wx.PaintEvent`.
        """

        dc = wx.BufferedPaintDC(self)
        self.PrepareDC(dc)

        dc.Clear()

        rowPos = colPos = 0

        size = self.GetClientSize()
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.Colour(200, 200, 200)))

        for row in range(self.rows):
            rowH = self.flexSizer.GetCellSize(row, 0)[1]
            rowPos += rowH + 10
            dc.DrawLine(0, rowPos, size.x, rowPos)

        for col in range(self.columns - 1):
            colW = self.flexSizer.GetCellSize(0, col)[0]
            colPos += colW + 10
            dc.DrawLine(colPos, 0, colPos, rowPos)

    def OnErase(self, event):
        """
        Handles the ``wx.EVT_ERASE_BACKGROUND`` event for `NotebookPage`.

        :param `event`: a `wx.EraseEvent`.
        """

        # This is intentionally empty, to reduce flicker.
        pass

    def ExportData(self):
        """ Exports the data contained in the notebook page to the clipboard. """

        children = self.GetChildren()
        numCols = self.columns
        numRows = len(children) / numCols

        clipboardString = ""
        for row in range(numRows):
            for col in range(numCols):
                itemIndex = numCols * row + col
                window = children[itemIndex]
                if isinstance(window, StaticText):
                    value = window.GetLabel()
                else:
                    value = window.GetValue()

                clipboardString += value + "\t"
            clipboardString += "\n"

        self.do = wx.TextDataObject()
        self.do.SetText(clipboardString)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.do)
            wx.TheClipboard.Close()
            return True
        else:
            return False


class AppearancePage(wx.Panel):
    """ A simple notebook page which holds widgets appearance on various platforms. """

    def __init__(self, parent, data):
        """
        Default class constructor.

        :param `parent`: parent window. Should not be ``None``;
        :param `data`: a dictionary of {"platform name": "image stream"} images to display.
        """

        wx.Panel.__init__(self, parent, size=(0, 0))

        self.SetBackgroundColour(wx.WHITE)
        self.SetData(data)

    def SetData(self, data):
        """
        Actually sets the data to be displayed.

        :param `data`: a dictionary of {"platform name": "image stream"} images to display.
        """

        lenPlat = len(_platformNames)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(2, lenPlat, 10, 10)

        boldFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont.SetWeight(wx.FONTWEIGHT_BOLD)
        backColour = self.GetBackgroundColour()

        mainSizer.Add((0, 0), 1, wx.EXPAND)

        unknownBmp = unknown.GetBitmap()

        for indx, plat in enumerate(_platformNames):
            if plat in data and data[plat] is not None:
                stream = data[plat]
                image = wx.Image(BytesIO(stream))
                bmp = wx.Bitmap(image)
                stBmp = wx.StaticBitmap(self, -1, bmp)
            else:
                stBmp = wx.StaticBitmap(self, -1, unknownBmp)

            sizer.Add(stBmp, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
            sizer.AddGrowableCol(indx)

        for plat in _platformNames:
            stText = StaticText(self, -1, plat, style=wx.ALIGN_CENTER)
            stText.SetFont(boldFont)
            stText.SetBackgroundColour(backColour)
            sizer.Add(stText, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        mainSizer.Add(sizer, 10, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        mainSizer.Add((0, 0), 2, wx.EXPAND)

        self.SetSizer(mainSizer)
        mainSizer.Layout()

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for `AppearancePage`.

        :param `event`: a `wx.SizeEvent`.
        """

        event.Skip()
        self.Refresh()


class TheDemo(wx.Frame):
    """ The main `TheDemo` application frame. """

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        """
        Default class constructor.

        :param `parent`: the window parent. This may be ``None``. If it is not ``None``, the
         frame will always be displayed on top of the parent window on Windows;
        :param `id`: the window identifier. It may take a value of -1 to indicate a default value;
        :param `title`: the caption to be displayed on the frame's title bar;
        :param `pos`: the window position. A value of (-1, -1) indicates a default position, chosen
         by either the windowing system or wxPython, depending on platform;
        :param `size`: the window size. A value of (-1, -1) indicates a default size, chosen by
         either the windowing system or wxPython, depending on platform;
        :param `style`: the window style.
        """

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        flags = self._mgr.GetAGWFlags()
        flags += aui.AUI_MGR_ALLOW_ACTIVE_PANE | aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_AERO_DOCKING_GUIDES | \
                 aui.AUI_MGR_SMOOTH_DOCKING

        self._mgr.SetAGWFlags(flags)

##        if wx.Platform == "__WXMSW__":
##            # Workaround a stupid bug in AUI...
##            try:
##                self._mgr.SetArtProvider(aui.ModernDockArt(self))
##            except NameError:
##                pass

        self.leftTree = CT.CustomTreeCtrl(self, -1, agwStyle=CT.TR_DEFAULT_STYLE |
                                          CT.TR_SINGLE | CT.TR_FULL_ROW_HIGHLIGHT |
                                          CT.TR_HIDE_ROOT)
        self.centerPanel = aui.AuiNotebook(self, -1, agwStyle=aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_WINDOWLIST_BUTTON |
                                           aui.AUI_NB_SMART_TABS | aui.AUI_NB_NO_TAB_FOCUS)

        self._mgr.AddPane(self.leftTree, aui.AuiPaneInfo().Name("Tree").
                          Caption("wxPython Widgets/Events").Left().MaximizeButton(True).
                          MinSize((230, 300)).CloseButton(False).MinimizeButton(True).
                          FloatingSize((300, 600)))
        self._mgr.AddPane(self.centerPanel, aui.AuiPaneInfo().Name("Notebook").
                          CenterPane())

        self.leftTree.SetBackgroundColour(wx.WHITE)
        self.centerPanel.SetUniformBitmapSize((16, 16))
        self.SetIcon(mondrian.GetIcon())

        try:
            dirName = os.path.dirname(os.path.abspath(__file__))
        except:
            dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.dirName = dirName
        self.lastSelection = None
        self.downloading = False

        self.GetPickledFile()
        self.CreateMenuBar()
        self.CreateBar()
        self.PopulateTree()
        self.BindEvents()
        self.LoadPreferences()

        self.Show()

    def LoadPreferences(self):
        """
        Reads the user's preferences (window size, position, layout, etc...) from the user's
        preferences folder.

        .. note:: On Windows, this folder is located here:

           ``C:\Users\USER_ID\AppData\Roaming\TheDemo\TheDemo_Options``
        """

        app = wx.GetApp()

        frame_pos = app.GetPreference('POSITION', default=None)
        frame_size = app.GetPreference('SIZE', default=None)
        maximize = app.GetPreference('MAXIMIZE', default=False)
        perspective = app.GetPreference('PERSPECTIVE', default='')

        if frame_size and frame_size[0] > 300 and frame_size[1] > 300:
            self.SetSize(frame_size)

        if frame_pos and frame_pos[0] > -10 and frame_pos[1] > -10:
            self.SetPosition(frame_pos)
        else:
            self.CenterOnScreen()

        if perspective:
            self._mgr.LoadPerspective(perspective)
            self._mgr.Update()

        if maximize:
            self.Maximize()

    def GetPickledFile(self):
        """ Returns the file where downloaded data is stored (if any). """

        pickledFile = os.path.join(self.dirName, __appname__ + ".pkl")
        if not os.path.isfile(pickledFile):
            self.pickledData = {}
            return

        fid = open(pickledFile, "rb")
        try:
            self.pickledData = cPickle.load(fid)
        except:
            self.pickledData = {}

        fid.close()

    def PopulateTree(self):
        """ Populates the left tree control with widget and event names. """

        imageList = wx.ImageList(16, 16)
        imageList.Add(question.GetBitmap())
        imageList.Add(down.GetBitmap())
        imageList.Add(error.GetBitmap())
        imageList.Add(method.GetBitmap())

        self.leftTree.AssignImageList(imageList)
        self.leftTree.SetIndent(10)
        self.leftTree.EnableSelectionVista()

        boldFont1 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldFont2 = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        mini_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        font_size = boldFont1.GetPointSize()
        boldFont1.SetPointSize(font_size + 1)
        boldFont1.SetWeight(wx.FONTWEIGHT_BOLD)
        boldFont2.SetWeight(wx.FONTWEIGHT_BOLD)
        mini_font.SetPointSize(font_size - 1)

        root = self.leftTree.AddRoot("Root")
        data = [("Widgets", _widgets), ("Events", _events)]

        for text, category in data:
            item = self.leftTree.AppendItem(root, text)
            self.leftTree.SetItemFont(item, boldFont1)
            keys = category.keys()
            keys.sort()
            for key in keys:
                subitem = self.leftTree.AppendItem(item, key.replace("1", ""))
                self.leftTree.SetItemFont(subitem, boldFont2)
                for klass in category[key]:
                    if klass in self.pickledData:
                        phoenix = self.pickledData[klass]
                        image = (phoenix.Any() and [1] or [2])[0]
                        child = self.leftTree.AppendItem(subitem, klass, image=image)
                        self.leftTree.SetPyData(child, phoenix)

                        for method_name, method_description in phoenix.GetMethods():
                            grand_child = self.leftTree.AppendItem(child, method_name, image=3)
                            self.leftTree.SetItemFont(grand_child, mini_font)

                    else:
                        child = self.leftTree.AppendItem(subitem, klass, image=0)

                subitem.Expand()

            item.Expand()

        root.Expand()

    def BindEvents(self):
        """ Binds the events for the main application. """

        self.leftTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)

        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.centerPanel.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def CreateMenuBar(self):
        """ Creates the menu bar for `TheDemo`. """

        # Prepare the menu bar
        menuBar = wx.MenuBar()

        # File menu
        fileMenu = wx.Menu()

        item = wx.MenuItem(fileMenu, ID_EXPORT, "&Export data to clipboard\tCtrl+E",
                           "Exports the current visible list of data to the clipboard")
        item.SetBitmap(clipboard.GetBitmap())
        fileMenu.Append(item)

        fileMenu.AppendSeparator()

        item = wx.MenuItem(fileMenu, wx.ID_DELETE, "&Delete stored data\tCtrl+D",
                           "Deletes the data already stored using cPickle")
        item.SetBitmap(delete.GetBitmap())
        fileMenu.Append(item)

        fileMenu.AppendSeparator()
        item = wx.MenuItem(fileMenu, wx.ID_EXIT, "&Exit\tCtrl+Q",
                           "Exit TheDemo application")
        item.SetBitmap(exit.GetBitmap())
        fileMenu.Append(item)

        # File menu
        helpMenu = wx.Menu()
        item = wx.MenuItem(helpMenu, wx.ID_ABOUT, "&About TheDemo...\tCtrl+A",
                           "Shows information about TheDemo")
        item.SetBitmap(about.GetBitmap())
        helpMenu.Append(item)

        # Add menus to the menu bar
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

    def CreateBar(self):
        """ Creates the status bar for `TheDemo`. """
        if 'phoenix' in wx.PlatformInfo:
            self.statusBar = self.CreateStatusBar(2, wx.STB_SIZEGRIP)
        else:
            self.statusBar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusBar.SetStatusWidths([-2, -1])
        self.FillStatusBar()

    def FillStatusBar(self):
        """ Fills the statusbar fields with different information. """

        # Get the wxPython version information
        wxPythonVersion = wx.version()
        statusText = "wxPython %s" % wxPythonVersion

        # Ah, by the way, thank you menu bar for deleting my status bar messages...
        self.statusBar.SetStatusText(statusText, 1)
        msg = "Welcome to TheDemo: (c) Andrea Gavana, 03 June 2009"
        self.statusBar.SetStatusText(msg, 0)

    def OnSelectionChanged(self, event):
        """
        Handles the ``wx.EVT_TREE_SEL_CHANGED`` event for the tree control.

        :param `event`: a `wx.TreeEvent`.
        """

        item = event.GetItem()
        event.Skip()

        children = self.leftTree.GetChildrenCount(item)
        if not self.leftTree.GetPyData(item) and children > 0:
            return

        if children == 0 and item.GetImage() == 3:
            # Inside methods
            self.currentItem = item.GetParent()
            method_name = item.GetText()
            self.DisplayHelp(method_name, self.leftTree.GetPyData(self.currentItem))
            return
        else:
            self.currentItem = item

        self.downloading = True

        data = self.leftTree.GetPyData(item)
        if data is not None:
            self.LoadData(data, item.GetText())
        else:
            klass = self.leftTree.GetItemText(item)
            parentText = self.leftTree.GetItemParent(item).GetText()
            if parentText != 'Core':
                klass = '%s.%s' % (parentText.lower(), klass)

            ReadStyleDocs(self, klass)

    def AddChildrenMethods(self, data):

        self.leftTree.SetPyData(self.currentItem, data)
        for method_name, method_description in data.GetMethods():
            self.leftTree.AppendItem(self.currentItem, method_name, image=3)

    def LoadData(self, data, classString=""):
        """
        Layouts the interface once new data are downloaded.

        :param `data`: the data to be displayed.
        """

        self.Freeze()
        pageTexts = []
        parentName = self.leftTree.GetItemParent(self.currentItem).GetText()

        if hasattr(self, 'dp'):
            self.db.mgr.UnInit()

        for indx in xrange(self.centerPanel.GetPageCount() - 1, -1, -1):
            self.centerPanel.DeletePage(indx)

        self.SetTitle("TheDemo v%s: %s documentation" % (__version__, self.currentItem.GetText()))
        self.downloading = False

        pageTexts.append("Demo")
        img1 = appearanceBmp.GetBitmap()
        self.dp = tdc.wxPythonDemo(self)
        self.centerPanel.AddPage(self.dp, "Demo", True, img1)
        self.dp.LoadDemo(classString)

        if data is None:
            self.centerPanel.AddPage(EmptyPage(self, "Unable to connect to the internet"), "No Connection",
                                     True, error.GetBitmap())
            self.Thaw()
            return

        if isinstance(data, basestring) or not data.Any():
##            self.leftTree.SetPyData(self.currentItem, PhoenixClass('__dummy__'))
            self.leftTree.SetItemImage(self.currentItem, 2)

            if not isinstance(data, basestring):
                msg = "No styles, events or control images have been found for class %s" % classString
            else:
                msg = data

            self.centerPanel.AddPage(EmptyPage(self, msg), "Not Found",
                                     True, error.GetBitmap())

            if not isinstance(data, basestring):
                self.AddChildrenMethods(data)

            self.Thaw()

            return

        self.leftTree.SetItemImage(self.currentItem, 1)
        self.AddChildrenMethods(data)

        img1, img2, img3 = stylesBmp.GetBitmap(), eventsBmp.GetBitmap(), extraBmp.GetBitmap()
        img4 = appearanceBmp.GetBitmap()

        if data.winStyles:
            pageTexts.append("Styles")
            self.centerPanel.AddPage(NotebookPage(self, data.winStyles, 3, parentName), "Styles",
                                     True, img1)
        if data.winExtra:
            pageTexts.append("Extra Styles")
            self.centerPanel.AddPage(NotebookPage(self, data.winExtra, 3, parentName), "Extra Styles",
                                     False, img3)
        if data.winEvents:
            pageTexts.append("Events")
            self.centerPanel.AddPage(NotebookPage(self, data.winEvents, 2, parentName), "Events", False, img2)

        if data.winAppearance:
            pageTexts.append("Appearance")
            self.centerPanel.AddPage(AppearancePage(self, data.winAppearance), "Appearance", False, img4)

        if self.lastSelection is None or self.lastSelection not in pageTexts:
            self.centerPanel.SetSelection(0)
        else:
            index = pageTexts.index(self.lastSelection)
            self.centerPanel.SetSelection(index)

        self.SendSizeEvent()
        self.Thaw()
        self.Refresh()
        self.Update()
        self.downloading = False

    def GetDemo(self, classString=""):
        """
        Load the demo and overview description.

        :param `classString`: the class name.
        """
        demo = 'demo'
        overview = 'overview'
        code = 'code'
        return demo, overview, code

    def DisplayHelp(self, method_name, parent_class):

        self.Freeze()
        css1, css2 = wx.GetApp().GetPhoenixCSS()

        for mn, md in parent_class.methods:
            if mn == method_name:
                break

        html = _html_template % (css1, css2, md)
        page = webview.WebView.New(self)
        page.SetBackgroundColour(wx.WHITE)
        page.SetPage(html, '')
        img = method.GetBitmap()
        self.centerPanel.AddPage(page, method_name, True, img)
        self.SendSizeEvent()
        self.Thaw()
        self.Refresh()
        self.Update()

    def RunError(self, kind, msg):
        """
        An utility method that shows a message dialog with different functionalities
        depending on the input.

        :param `kind`: the kind of message (error, warning, question, message);
        :param `msg`: the actual message to display.
        """

        kindDict = {0: "Message", 1: "Warning", 2: "Error", 3: "Question"}
        kind = kindDict[kind]

        if kind == "Message":    # is a simple message
            style = wx.OK | wx.ICON_INFORMATION
        elif kind == "Warning":  # is a warning
            style = wx.OK | wx.ICON_EXCLAMATION
        elif kind == "Question":  # is a question
            style = wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
        else:                    # is an error
            style = wx.OK | wx.ICON_ERROR

        # Create the message dialog
        dlg = GMD.GenericMessageDialog(self, msg, "TheDemo %s" % kind, style)
        dlg.SetIcon(self.GetIcon())
        answer = dlg.ShowModal()
        dlg.Destroy()

        if kind == "Question":
            # return the answer, it was a question
            return answer

    def OnUpdateUI(self, event):
        """
        Handles the ``wx.EVT_UPDATE_UI`` event for the main frame.

        :param `event`: a `wx.UpdateUIEvent`.
        """

        evId = event.GetId()
        if evId == ID_EXPORT:
            enable = self.centerPanel.GetPageCount() > 0 and \
                self.lastSelection != "Appearance"
            event.Enable(enable)

    def OnPageChanged(self, event):
        """
        Handles the ``wx.lib.agw.aui.EVT_AUINOTEBOOK_PAGE_CHANGED`` event for the notenbook.

        :param `event`: a `wx.lib.agw.aui.AuiNotebookEvent`.
        """

        event.Skip()

        if not self.downloading:
            self.lastSelection = self.centerPanel.GetPageText(event.GetSelection())

    def OnExport(self, event):
        """
        Handles the ``ID_EXPORT`` menu item event.

        :param `event`: a `wx.MenuEvent`.
        """

        page = self.centerPanel.GetPage(self.centerPanel.GetSelection())
        if page.ExportData():
            self.RunError(0, "Data successfully exported to the clipboard.")
        else:
            self.RunError(2, "Unable to copy data to the clipboard... Sorry.")

    def OnDelete(self, event):
        """
        Handles the ``wx.ID_DELETE`` menu item event.

        :param `event`: a `wx.MenuEvent`.
        """

        msg = "Are you sure you wish to delete all the downloaded data?"
        answer = self.RunError(3, msg)

        if answer != wx.ID_YES:
            return

        img = mondrian.GetBitmap().ConvertToImage().Scale(16, 16)
        busy = PBI.PyBusyInfo("Deleting downloaded data...", parent=self,
                              title="TheDemo is busy", icon=img.ConvertToBitmap())

        wx.SafeYield()

        pickledFile = os.path.join(self.dirName, __appname__ + ".pkl")
        if os.path.isfile(pickledFile):
            os.remove(pickledFile)

        self.RecurseOnChildren(item=None, pickledData=None, setData=True)
        del busy

    def OnClose(self, event):
        """
        Handles the ``wx.ID_EXIT`` menu item event and the `wx.CloseEvent`.

        :param `event`: a `wx.MenuEvent` or a `wx.CloseEvent`.
        """

        img = mondrian.GetBitmap().ConvertToImage().Scale(16, 16)
        busy = PBI.PyBusyInfo("Saving downloaded data...", parent=self,
                              title="TheDemo is closing", icon=img.ConvertToBitmap())

        wx.SafeYield()

        pickledFile = os.path.join(self.dirName, __appname__ + ".pkl")
        pickledData = self.RecurseOnChildren(item=None, pickledData=None)

        fid = open(pickledFile, "wb")
        cPickle.dump(pickledData, fid, cPickle.HIGHEST_PROTOCOL)
        fid.close()

        app = wx.GetApp()

        pos = self.GetPosition()
        size = self.GetSize()
        if pos.x > -10 and pos.y > -10:
            app.SetPreference('POSITION', self.GetPosition())

        if size.x > 300 and size.y > 300:
            app.SetPreference('SIZE', self.GetSize())

        app.SetPreference('MAXIMIZE', self.IsMaximized())
        app.SetPreference('PERSPECTIVE', self._mgr.SavePerspective())

        del busy
        wx.CallAfter(self.Destroy)

    def RecurseOnChildren(self, item, pickledData, setData=False):
        """
        Recurse on all items of the tree control, setting data on them
        or deleting data from them, depending on the value of the
        `setData` parameter.

        :param `item`: the tree item: if ``None``, the root item is used;
        :param `pickledData`: a dictionary which holds the stored data;
        :param `setData`: whether to set the data or to retrieve them.
        """

        if item is None:
            item = self.leftTree.GetRootItem()
        if pickledData is None:
            pickledData = {}

        child, cookie = self.leftTree.GetFirstChild(item)
        while child:
            if not self.leftTree.GetPyData(child):
                pickledData = self.RecurseOnChildren(child, pickledData, setData)
            else:
                if setData:
                    self.leftTree.SetPyData(child, None)
                    self.leftTree.SetItemImage(child, 0)
                else:
                    text = self.leftTree.GetItemText(child)
                    pydata = self.leftTree.GetPyData(child)
                    if pydata is not None:
                        pickledData[text] = pydata

            child, cookie = self.leftTree.GetNextChild(item, cookie)

        return pickledData

    def OnAbout(self, event):
        """ Shows the about dialog for `TheDemo`. """

        msg = ("This is the about dialog of TheDemo.\n\n" +
              "Version %s \n" +
              "Author: Andrea Gavana @ 03 Jun 2009\n\n" +
              "Please report any bug/request of improvements\n" +
              "to me at the following addresses:\n\n" +
              "andrea.gavana@gmail.com\nandrea.gavana@maerskoil.com") % __version__

        self.RunError(0, msg)


class TheDemoApp(wx.App):
    """
    This class represents the application and is used to:

    1. Bootstrap the wxPython system and initialize the underlying GUI toolkit;
    2. Set and get application-wide properties;
    3. Implement the native windowing system main message or event loop, and to
       dispatch events to window instances.

    Every wx application must have a single `wx.App` instance, and all creation
    of UI objects should be delayed until after the `wx.App` object has been
    created in order to ensure that the gui platform and wxPython have been fully
    initialized.
    """

    def __init__(self):
        """
        Default class constructor.
        """

        wx.App.__init__(self, False)

    def OnInit(self):
        """
        This method must be provided by the application, and will usually create
        the application's main window, optionally calling `SetTopWindow()`.

        You may use :meth:`OnExit` to clean up anything initialized here, provided
        that the function returns ``True``.

        :returns: ``True`` to continue processing, ``False`` to exit the application immediately.
        :rtype: `bool`
        """

        self.user_preferences = None
        self.phoenix_css = []

        self.SetAppName('TheDemo')
        self.frame = TheDemo(None, -1, "TheDemo v%s" % __version__, size=(950, 750))
        self.SetTopWindow(self.frame)

        return True

    def GetDataDir(self):
        """
        Returns the option directory for :mod:`TheDemo`.

        :rtype: `string`
        """

        sp = wx.StandardPaths.Get()
        return sp.GetUserDataDir()

    def GetConfig(self):
        """
        Returns the configuration for :mod:`TheDemo`.

        :rtype: `wx.FileConfig`
        """

        if self.user_preferences is not None:
            return self.user_preferences

        if not os.path.exists(self.GetDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.GetDataDir())

        self.user_preferences = wx.FileConfig(localFilename=os.path.join(self.GetDataDir(), 'TheDemo_Options'))
        return self.user_preferences

    def GetPreference(self, preferenceKey=None, default=None):
        """
        Returns the user preferences as stored in `wx.Config`.

        :param string `preferenceKey`: the preference to load.

        :rtype: Any Python object that is convertible to string.
        """

        user_preferences = self.GetConfig()
        val = user_preferences.Read(preferenceKey)
        if not val:
            self.SetPreference(preferenceKey, default)
            return default

        try:
            ret_val = eval(val)
        except (SyntaxError, NameError):
            ret_val = val

        return ret_val

    def SetPreference(self, preferenceKey, value):
        """
        Saves the user preferences in `wx.Config`.

        :param string `newPreferences`: the new preferences to save;
        :param `value`: the new value to save, it can be any Python
         object that is convertible to a string.
        """

        user_preferences = self.GetConfig()
        user_preferences.Write(preferenceKey, str(value))
        user_preferences.Flush()

    def GetPhoenixCSS(self):
        """
        Returns the css files for :mod:`TheDemo`.

        :rtype: `tuple`
        """

        if self.phoenix_css:
            return self.phoenix_css

        if not os.path.exists(self.GetDataDir()):
            # Create the data folder, it still doesn't exist
            os.makedirs(self.GetDataDir())

        for css in _css_files:

            filename = os.path.join(self.GetDataDir(), css + '.css')

            if os.path.isfile(filename):
                if css.startswith('p'):
                    self.phoenix_css.append(filename)
                continue

            url = _cssURL % css + '.css'
            fid = urllib.request.urlopen(url)
            css_text = fid.read()
            fid2 = open(filename, 'wt')
            fid2.write(css_text)
            fid2.close()

            if css.startswith('p'):
                self.phoenix_css.append(filename)

        return self.phoenix_css


# Run the main application
if __name__ == "__main__":

    app = TheDemoApp()
    app.MainLoop()
