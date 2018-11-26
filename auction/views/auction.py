import wx
import sys
import platform
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from auction.views.team import ViewTeam
from auction.views.styles import DD, ACV, ACVE


class ViewAuction(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewAuction, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelAuction(parent=self)
        self.panel.btn_save.Disable()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        size = (450, 700) if platform.system() == 'Linux' else (350, 600)
        self.SetSize(size)
        self.SetSizer(sizer)
        self.Centre()
        self.bind_widgets()

    def bind_widgets(self):
        self.Bind(wx.EVT_CLOSE, self.on_quit)  # top bar close event
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.buy_player, self.panel.btn_save)
        self.Bind(wx.EVT_RADIOBOX, self.on_player_filters)
        self.Bind(wx.EVT_COMBOBOX, self.on_player_filters,
                  self.panel.cb_real_teams)
        self.Bind(wx.EVT_COMBOBOX, self.on_player, self.panel.cb_players)
        self.Bind(wx.EVT_COMBOBOX, self.on_buyer, self.panel.cb_teams)

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_buyer(self, event):
        team_name = self.panel.cb_teams.GetStringSelection()
        team = self.controller.get_team(team_name)
        role = self.panel.rb_roles.GetStringSelection()
        players_bought = team.get_players_bought_by_role(role)
        if role == 'goalkeeper':
            max_players = team.max_goalkeepers
        elif role == 'defender':
            max_players = team.max_defenders
        elif role == 'midfielder':
            max_players = team.max_midfielders
        else:
            max_players = team.max_forwards

        if max_players - players_bought > 0:
            self.panel.btn_save.Enable()
        else:
            self.show_message('No slot for this player!')
            self.panel.btn_save.Disable()

    # noinspection PyUnusedLocal
    def buy_player(self, event):
        player_name = self.panel.cb_players.GetStringSelection()
        auction_value = self.panel.auction_value.GetValue()
        buyer = self.panel.cb_teams.GetStringSelection()
        print("   INFO: %s --> %s: " % (player_name, auction_value))
        if not auction_value:
            self.show_message('Missing auction value!')
        else:
            if not buyer:
                self.show_message('Missing Team, please choose a buyer')
            else:
                team = self.controller.get_team(buyer)
                to_buy = team.get_max_players() - sum(team.get_players_bought())
                remain = team.budget - int(auction_value) - to_buy
                if remain >= 0:
                    msg = self.controller.buy_player(player_name,
                                                     auction_value, buyer)
                    self.show_message('Player %s bought!' % player_name)
                    self.clear_fields()
                    self.panel.cb_real_teams.SetValue('')
                    self.panel.cb_players.SetValue('')
                    self.panel.cb_teams.SetValue('')
                else:
                    self.show_message('Not enough money!')

    def clear_fields(self):
        self.panel.name.SetLabel("")
        self.panel.code.SetLabel("")
        self.panel.real_team.SetLabel("")
        self.panel.value.SetLabel("")
        self.panel.auction_value.SetValue('')

    # noinspection PyUnusedLocal
    def on_player_filters(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        real_team = self.panel.cb_real_teams.GetStringSelection()
        players = self.controller.get_players(role=role, real_team=real_team)
        self.update_choice_players(players)
        self.clear_fields()
        self.panel.cb_players.SetValue('')
        self.panel.cb_teams.SetValue('')


    # noinspection PyUnusedLocal
    def on_player(self, event):
        player_name = self.panel.cb_players.GetStringSelection()
        player = self.controller.get_player_by_name(player_name)
        self.update_player(player)

    def update_choice_players(self, players):
        self.panel.cb_players.Clear()
        self.panel.cb_players.AppendItems(players)

    def update_player(self, player):
        self.panel.name.SetLabel(player.name)
        self.panel.code.SetLabel(str(player.code))
        self.panel.value.SetLabel(str(player.cost))
        self.panel.real_team.SetLabel(player.real_team)
        if not player.auction_value:
            self.panel.auction_value.SetLabel("")
        else:
            self.panel.auction_value.SetLabel(str(player.auction_value))
        if player.team:
            self.panel.cb_teams.SetValue(player.team.name)
        else:
            self.panel.cb_teams.Clear()
            teams = self.controller.get_teams()
            if not teams:
                self.show_message('No teams found, please create them before')
                self.panel.btn_save.Disable()
            else:
                self.panel.cb_teams.AppendItems(teams)
                self.panel.btn_save.Enable()

    def update_choice_real_teams(self, real_teams):
        self.panel.cb_real_teams.Clear()
        self.panel.cb_real_teams.AppendItems(real_teams)

    @staticmethod
    def show_message(string):
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)


class PanelAuction(wx.Panel):
    def __init__(self, parent):
        super(PanelAuction, self).__init__(parent)
        roles = ['goalkeeper', 'defender', 'midfielder', 'forward']
        real_teams = parent.controller.get_real_teams()
        self.name = wx.StaticText(self, size=(60, 20))
        self.code = wx.StaticText(self, size=(60, 20))
        self.real_team = wx.StaticText(self, size=(60, 20))
        self.value = wx.StaticText(self, size=(60, 20))
        self.auction_value = wx.TextCtrl(self)
        self.cb_real_teams = wx.ComboBox(self, -1, choices=real_teams, style=DD)
        self.cb_players = wx.ComboBox(self, -1, choices=[], style=DD)
        self.cb_teams = wx.ComboBox(self, -1, choices=[], style=DD)
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)

        # RADIO BUTTON sizer
        box_roles = wx.BoxSizer(wx.VERTICAL)
        box_roles.Add(self.rb_roles, 0, wx.ALIGN_CENTER_HORIZONTAL, 15)
        # SECOND sizer
        shortcut_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=5, vgap=5)
        shortcut_sizer.Add(wx.StaticText(self, label="Real team"), 1, ACVE, 5)
        shortcut_sizer.Add(self.cb_real_teams, 0, ACVE)
        shortcut_sizer.Add(wx.StaticText(self, label="Player"), 1, ACVE, 5)
        shortcut_sizer.Add(self.cb_players, 0, ACVE)
        # THIRD sizer
        text_sizer = wx.FlexGridSizer(rows=8, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Name:"), 0, ACV)
        text_sizer.Add(self.name, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Code:"), 0, ACV)
        text_sizer.Add(self.code, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Real team:"), 0, ACV)
        text_sizer.Add(self.real_team, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Value:"), 0, ACV)
        text_sizer.Add(self.value, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Cost:"), 0, ACV)
        text_sizer.Add(self.auction_value, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Buyer:"), 0, ACV)
        text_sizer.Add(self.cb_teams, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)
        # BUTTON Sizer
        button_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, wx.ID_SAVE, label="SAVE")
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="QUIT")
        self.btn_save.SetDefault()
        button_sizer.AddButton(self.btn_save)
        button_sizer.AddButton(self.btn_quit)
        # WRAPPER Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_roles, 0, wx.EXPAND | wx.ALL, 20)
        sizer.Add(shortcut_sizer, 0, wx.EXPAND | wx.ALL, 20)
        sizer.Add(text_sizer, 0, wx.EXPAND | wx.ALL, 20)
        sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 20)
        button_sizer.Realize()

        self.SetSizer(sizer)
        self.SetBackgroundColour('Pink')


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class ViewAuctionSummary(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewAuctionSummary, self).__init__(parent=self.parent,
                                                 title=title)
        self.controller = self.parent.controller
        self.panel = PanelAuctionSummary(parent=self)
        teams = self.controller.get_teams()
        self.fill_team_list(teams)
        size = (850, 500) if platform.system() == 'Linux' else (750, 400)
        self.SetSize(size)
        self.Centre()
        self.bind_widgets()  # Bind widgets

    def bind_widgets(self):
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list,
                  self.panel.team_list)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_list(self, event):
        item_id = event.GetIndex() if wx.version().startswith('4') else \
            event.m_itemIndex
        team_name = self.panel.team_list.GetItemText(item_id)
        team = self.controller.get_team(team_name)
        self.controller.set_temporary_object(team)
        gk, df, md, fw = team.get_players_bought()
        # here I open edit frame to change fuel object see pcbhandler for ex.
        view_edit = ViewTeam(self.parent, "Edit Team", is_editor=True)
        view_edit.panel.cb_teams.Disable()
        view_edit.panel.name.SetValue(team.name)
        view_edit.panel.budget.ChangeValue(str(team.budget))
        view_edit.panel.remaining_gk.ChangeValue(str(team.max_goalkeepers - gk))
        view_edit.panel.remaining_def.ChangeValue(str(team.max_defenders - df))
        view_edit.panel.remaining_mid.ChangeValue(str(
            team.max_midfielders - md))
        view_edit.panel.remaining_fw.ChangeValue(str(team.max_forwards - fw))
        view_edit.panel.trades.ChangeValue(str(team.max_trades))
        view_edit.panel.btn_delete.Enable()
        view_edit.SetWindowStyle(wx.STAY_ON_TOP)

    def fill_team_list(self, teams):
        for team_name in teams:
            team = self.controller.get_team(team_name)
            insert_item = self.panel.team_list.InsertStringItem
            set_item = self.panel.team_list.SetStringItem
            if wx.version().startswith('4'):
                insert_item = self.panel.team_list.InsertItem
                set_item = self.panel.team_list.SetItem

            index = insert_item(sys.maxsize, str(team.name))
            set_item(index, 1, str(team.budget))
            gk, df, mf, fw = team.get_players_bought()
            set_item(index, 2, str(team.max_goalkeepers - gk))
            set_item(index, 3, str(team.max_defenders - df))
            set_item(index, 4, str(team.max_midfielders - mf))
            set_item(index, 5, str(team.max_forwards - fw))
            set_item(index, 6, str(team.max_trades))

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        self.panel.team_list.DeleteAllItems()
        teams = self.controller.get_teams()
        self.fill_team_list(teams)

    @staticmethod
    def show_message(string):
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)


class PanelAuctionSummary(wx.Panel):
    def __init__(self, parent):
        super(PanelAuctionSummary, self).__init__(parent=parent)

        self.team_list = AutoWidthListCtrl(self)
        self.team_list.InsertColumn(0, 'name', wx.LIST_FORMAT_RIGHT, 125)
        self.team_list.InsertColumn(1, 'budget', width=50)
        self.team_list.InsertColumn(2, 'remaining gk', width=100)
        self.team_list.InsertColumn(3, 'remaining def', width=100)
        self.team_list.InsertColumn(4, 'remaining mid', width=100)
        self.team_list.InsertColumn(5, 'remaining fw', width=100)
        self.team_list.InsertColumn(6, 'remaining trades', width=100)

        team_list_box = wx.BoxSizer(wx.HORIZONTAL)
        team_list_box.Add(self.team_list, 1, wx.EXPAND)
        btn_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="QUIT")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="REFRESH")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(team_list_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
