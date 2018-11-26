# -*- coding: utf-8 -*-#
import wx
import wx.html as wxhtml
import platform
from auction.views.htmltext import ABOUT, HELP


class EntryDialog(wx.TextEntryDialog):
    """Simple Text Entry Dialog"""
    def __init__(self, parent, msg, value):
        super(EntryDialog, self).__init__(parent, msg, 'Core request',
                                          defaultValue=value, style=wx.OK)

    def get_choice(self):
        """get the state of the user choice"""
        if self.ShowModal() == wx.ID_OK:
            response = self.GetValue()
            self.Destroy()
            return response


class InfoFrame(wx.Frame):
    """Frame for Abuot text"""
    def __init__(self, parent, title):
        super(InfoFrame, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.text = ABOUT
        size = (450, 800) if platform.system() == 'Linux' else (400, 600)
        self.SetSize(size)
        html = wxhtml.HtmlWindow(self)
        html.SetPage(self.text)
        self.btn_quit = wx.Button(self, -1, 'quit', (25, 150), (150, -1))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn_quit, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.btn_quit)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()


class HelpFrame(wx.Frame):
    """Frame for Abuot text"""
    def __init__(self, parent, title):
        super(HelpFrame, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.text = HELP
        self.SetSize((600, 800))
        html = wxhtml.HtmlWindow(self)
        html.SetPage(self.text)
        self.btn_quit = wx.Button(self, -1, 'quit', (25, 150), (150, -1))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn_quit, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.btn_quit)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()
