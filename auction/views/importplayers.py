import wx
import os
import platform
from auction.views.styles import YN, OK, ACV


if platform.system() == 'Linux':
    IMPORT_PATH = r'/auction/days/'
else:
    IMPORT_PATH = r'\\auction\\days\\'


class ViewImportPlayers(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewImportPlayers, self).__init__(parent=self.parent,
                                                title=title)
        self.controller = self.parent.controller
        self.panel = PanelImportPlayers(parent=self)
        self.pb = None
        size = (400, 400) if platform.system() == 'Linux' else (300, 250)
        self.SetSize(size)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_import, self.panel.btn_import)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_import(self, event):
        choice = wx.MessageBox('Deleting All Players?', 'warning', YN)
        if choice == wx.YES:
            browser = FileBrowser(parent=self)
            path = browser.GetPath()
            try:
                with open(path) as txt_file:
                    data = txt_file.readlines()
                    max_limit = len(data)
                self.panel.status.set_range(len(data))
                if path:
                    self.controller.delete_players()
                    count = 1
                    for record in data:
                        self.panel.status.set_progress(count)
                        self.panel.status.SetLabel('elaborating %s' % count)
                        wx.MicroSleep(5)
                        print("   INFO: import record <%s>" % record.strip())
                        p = self.controller.import_player_bulk(record)
                        self.Update()
                        count += 1
                    self.panel.status.SetLabel('Done!')
                    self.controller.commit_all_players()
                    wx.MessageBox('Players successfully imported!', '', OK)
                    n_players = self.controller.get_players_count()
                    self.panel.n_players.SetLabel(str(n_players))
            except IOError:
                print("   INFO: Import operation aborted!")


class PanelImportPlayers(wx.Panel):
    def __init__(self, parent):
        super(PanelImportPlayers, self).__init__(parent)
        self.status = ProgressStatusBar(self)
        # style shortcuts
        n_players = parent.controller.get_players_count()
        self.n_players = wx.StaticText(self, label=str(n_players))
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_import = wx.Button(self, label='Import')
        # Layout
        text_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=8, vgap=8)
        text_sizer.Add(wx.StaticText(
            self, label="Players present in database:"), 0, ACV)
        text_sizer.Add(self.n_players, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)
        # wrapper sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn_import, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn_quit, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.status, 0, wx.EXPAND | wx.ALL, 5)
        self.SetBackgroundColour('Pink')
        self.SetSizer(sizer)


class FileBrowser(wx.FileDialog):
    def __init__(self, parent, ddir=os.getcwd()):
        wildcard = "File Evaluations (*.txt)|*.txt|" "Tutti i files (*.*)|*.*"
        super(FileBrowser, self).__init__(parent=parent, message='',
                                          defaultDir=ddir + IMPORT_PATH,
                                          wildcard=wildcard, style=wx.FD_OPEN)
        self.ShowModal()


class ProgressStatusBar(wx.StatusBar):
    """Custom StatusBar with a built-in progress bar"""
    def __init__(self, parent, id_=wx.ID_ANY, style=wx.SB_FLAT,
                 name='ProgressStatusBar'):
        super(ProgressStatusBar, self).__init__(parent, id_, style, name)
        self._changed = False
        self.busy = False
        self.timer = wx.Timer(self)
        self.progress_bar = wx.Gauge(self, style=wx.GA_HORIZONTAL)
        self.progress_bar.Hide()

        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 155])
        # self.SetBackgroundColour('Pink')

        self.Bind(wx.EVT_IDLE, lambda evt: self.__reposition())
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def __del__(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def __reposition(self):
        """Repositions the gauge as necessary"""
        if self._changed:
            field = self.GetFieldsCount() - 1
            rect = self.GetFieldRect(field)
            progress_bar_pos = (rect.x + 2, rect.y + 2)
            self.progress_bar.SetPosition(progress_bar_pos)
            progress_bar_size = (rect.width - 8, rect.height - 4)
            self.progress_bar.SetSize(progress_bar_size)
        self._changed = False

    # noinspection PyUnusedLocal
    def on_size(self, evt):
        self._changed = True
        self.__reposition()
        evt.Skip()

    # noinspection PyUnusedLocal
    def on_timer(self, evt):
        if not self.progress_bar.IsShown():
            self.timer.Stop()
        if self.busy:
            self.progress_bar.Pulse()

    def run(self, rate=100):
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def get_progress(self):
        return self.progress_bar.GetValue()

    def set_progress(self, val):
        if not self.progress_bar.IsShown():
            self.show_progress(True)

        if val == self.progress_bar.GetRange():
            self.progress_bar.SetValue(0)
            self.show_progress(False)
        else:
            self.progress_bar.SetValue(val)

    def set_range(self, val):
        if val != self.progress_bar.GetRange():
            self.progress_bar.SetRange(val)

    def show_progress(self, show=True):
        self.__reposition()
        self.progress_bar.Show(show)

    def start_busy(self, rate=100):
        self.busy = True
        self.__reposition()
        self.show_progress(True)
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def stop_busy(self):
        self.timer.Stop()
        self.show_progress(False)
        self.progress_bar.SetValue(0)
        self.busy = False

    def is_busy(self):
        return self.busy
