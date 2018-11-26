import platform
import wx
from auction.views.team import ViewTeam
from auction.views.trade import ViewTrade
from auction.views.player import ViewPlayer, ViewPlayerSummary
from auction.views.importplayers import ViewImportPlayers
from auction.views.auction import ViewAuction, ViewAuctionSummary
from auction.views.info import InfoFrame, HelpFrame
from auction.views.styles import OK


IMAGE_PATH = 'auction/views/images/' if platform.system() == 'Linux' else\
             'auction\\views\\images\\'


class Core(wx.Frame):
    def __init__(self, parent, controller, title):
        super(Core, self).__init__(parent=parent, title=title)
        self.controller = controller
        self.panel = wx.Panel(self)
        self.status_bar = wx.StatusBar(self.panel)
        self.menu_bar = wx.MenuBar()
        self.SetMenuBar(self.menu_bar)
        img = wx.Image('{}Fantacalcio.bmp'.format(IMAGE_PATH),
                       wx.BITMAP_TYPE_ANY)
        bitmap = wx.Bitmap(img) if wx.version().startswith('4') else \
            wx.BitmapFromImage(img)
        sb = wx.StaticBitmap(self.panel, -1, bitmap)
        # resize the frame on pict. size plus height of menu_bar and status_bar
        self.SetSize((sb.GetSize().x, sb.GetSize().y +
                      self.status_bar.GetSize().y * 2))
        self.panel.SetBackgroundColour('Pink')
        # Menu definition ------------------------------------------------------
        # AUCTION Menu ---------------------------------------------------------
        auction_menu = wx.Menu()
        self.menu_bar.Append(auction_menu, "Auction")
        self.new_auction_menu = auction_menu.Append(200, "New Auction")
        self.auction_summary = auction_menu.Append(201, "Auction Summary")
        auction_menu.AppendSeparator()
#        self.export_xls_menu = auction_menu.Append(-1, "Export to excel")
        self.export_csv_menu = auction_menu.Append(202, "Export to csv")
        auction_menu.AppendSeparator()
        self.exit_menu = auction_menu.Append(203, "Exit")
        # TEAM Menu ------------------------------------------------------------
        self.team_menu = wx.Menu()
        self.menu_bar.Append(self.team_menu, "Teams")
        self.new_team_menu = self.team_menu.Append(204, "New Team")
        self.edit_team_menu = self.team_menu.Append(205, "Edit Team")
        self.team_menu.AppendSeparator()
        self.trades_menu = self.team_menu.Append(206, "Trades")
        # PLAYER Menu ----------------------------------------------------------
        player_menu = wx.Menu()
        self.menu_bar.Append(player_menu, "Players")
        self.import_player_menu = player_menu.Append(207, "Import Players")
        player_menu.AppendSeparator()
        self.new_player_menu = player_menu.Append(208, "New Player")
        self.edit_player_menu = player_menu.Append(209, "Edit Player")
        player_menu.AppendSeparator()
        self.edit_player_summary_menu = player_menu.Append(210,
                                                           "Players Summary")
        # Info Menu ----------------------------------------------------------
        info_menu = wx.Menu()
        self.menu_bar.Append(info_menu, "Info")
        self.about_menu = info_menu.Append(211, "About...")
        self.guide_menu = info_menu.Append(212, "Auction 2.0 guide")

        # Menu bindings --------------------------------------------------------
        self.Bind(wx.EVT_MENU, self.quit, self.exit_menu)

        self.Bind(wx.EVT_MENU, self.on_new_auction, self.new_auction_menu)
        self.Bind(wx.EVT_MENU, self.on_auction_summary, self.auction_summary)

#        self.Bind(wx.EVT_MENU, self.on_export_to_xls, self.export_xls_menu)
        self.Bind(wx.EVT_MENU, self.on_export_to_csv, self.export_csv_menu)
        self.Bind(wx.EVT_MENU, self.new_team, self.new_team_menu)
        self.Bind(wx.EVT_MENU, self.edit_team, self.edit_team_menu)
        self.Bind(wx.EVT_MENU, self.on_trades, self.trades_menu)

        self.Bind(wx.EVT_MENU, self.on_import_players, self.import_player_menu)
        self.Bind(wx.EVT_MENU, self.new_player, self.new_player_menu)
        self.Bind(wx.EVT_MENU, self.edit_player, self.edit_player_menu)
        self.Bind(wx.EVT_MENU, self.player_summary,
                  self.edit_player_summary_menu)
        self.Bind(wx.EVT_MENU, self.on_about, self.about_menu)
        self.Bind(wx.EVT_MENU, self.on_guide, self.guide_menu)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 0, wx.EXPAND)
        sizer.Add(self.status_bar, 0, wx.EXPAND)
        self.SetSizer(sizer)

        self.Centre()

    # noinspection PyUnusedLocal
    def quit(self, event):
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_new_auction(self, event):
        if not self.controller.get_players_count():
            wx.MessageBox('No players in database, please import them before!',
                          '', OK)
        elif self.controller.get_teams_count() < 2:
            wx.MessageBox('Please create at least 2 teams to start auction',
                          '', OK)
        else:
            self.Disable()
            child = ViewAuction(parent=self, title='Auction')
            child.Show()

    # noinspection PyUnusedLocal
    def on_auction_summary(self, event):
        self.Disable()
        child = ViewAuctionSummary(parent=self, title='Auction Summary')
        child.Show()

    # noinspection PyUnusedLocal
    def new_team(self, event):
        self.Disable()
        child = ViewTeam(parent=self, title='New Team', is_editor=False)
        child.Show()

    # noinspection PyUnusedLocal
    def edit_team(self, event):
        self.Disable()
        child = ViewTeam(parent=self, title='Edit Team', is_editor=True)
        child.Show()

    # noinspection PyUnusedLocal
    def on_trades(self, event):
        self.Disable()
        child = ViewTrade(parent=self, title='Trade operations')
        child.Show()

    # noinspection PyUnusedLocal
    def on_import_players(self, event):
        self.Disable()
        child = ViewImportPlayers(parent=self, title='Import Players')
        child.Show()

    # noinspection PyUnusedLocal
    def edit_player(self, event):
        self.Disable()
        child = ViewPlayer(parent=self, title='Edit Player', is_editor=True)
        child.Show()

    # noinspection PyUnusedLocal
    def new_player(self, event):
        self.Disable()
        child = ViewPlayer(parent=self, title='New Player')
        child.Show()

    # noinspection PyUnusedLocal
    def player_summary(self, event):
        self.Disable()
        child = ViewPlayerSummary(parent=self, title='Players Summary')
        child.Show()

    # noinspection PyUnusedLocal
    def on_export_to_xls(self, event):
        pass

    # noinspection PyUnusedLocal
    def on_export_to_csv(self, event):
        self.controller.export_to_csv()

    # noinspection PyUnusedLocal
    def on_about(self, event):
        self.Disable()
        child = InfoFrame(parent=self, title='about Auction 2.0')
        child.Show()

    # noinspection PyUnusedLocal
    def on_guide(self, event):
        self.Disable()
        child = HelpFrame(parent=self, title='Auction 2.0 guide')
        child.Show()

    @staticmethod
    def show_message(string):
        wx.MessageBox(string, '', OK)
