import wx
import sys
import platform
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from auction.views.styles import OK, ACV, YN, DD


class ViewTeam(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        super(ViewTeam, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.is_editor = is_editor
        self.controller = self.parent.controller
        self.panel = PanelTeam(parent=self)
        size = (450, 800) if platform.system() == 'Linux' else (350, 650)
        self.SetSize(size)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.panel.btn_delete.Disable()
        if not self.is_editor:
            self.panel.cb_teams.Disable()
            self.panel.rb_roles.Disable()
            self.panel.player_list.Disable()
        else:
            for w in [w for w in self.panel.GetChildren()
                      if isinstance(w, wx.TextCtrl)]:
                w.SetValue('')

        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_COMBOBOX, self.on_team, self.panel.cb_teams)
        self.Bind(wx.EVT_RADIOBOX, self.on_roles, self.panel.rb_roles)
        self.Bind(wx.EVT_BUTTON, self.delete_team, self.panel.btn_delete)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.discard,
                  self.panel.player_list)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_team(self, event):
        team_name = self.panel.cb_teams.GetValue()
        team = self.controller.get_team(team_name)
        role = self.panel.rb_roles.GetStringSelection()
        self.controller.set_temporary_object(team)
        self.panel.name.SetValue(team.name)
        self.panel.trades.SetValue(str(team.max_trades))
        self.panel.budget.SetValue(str(team.budget))
        # get remaining players per role
        self.update_remaining_players(team)
        self.fill_players(self.controller.get_team_players(team_name, role))

    # noinspection PyUnusedLocal
    def discard(self, event):
            item_id = event.m_itemIndex
            code = self.panel.player_list.GetItemText(item_id)
            choice = wx.MessageBox('Discard player %s: '
                                   'are you sure?' % code, 'warning', YN)
            if choice == wx.YES:
                self.controller.discard_player(code)
                wx.MessageBox('Player and team budget updated', 'core info', OK)
                self.refresh_frame()

    def refresh_frame(self):
        team_name = self.panel.cb_teams.GetValue()
        team = self.controller.get_team(team_name)
        self.panel.budget.SetValue(str(team.budget))
        self.update_remaining_players(team)
        role = self.panel.rb_roles.GetStringSelection()
        self.fill_players(self.controller.get_team_players(team_name, role))

    def update_remaining_players(self, team):
        gk, df, mf, fw = team.get_players_bought()
        self.panel.remaining_gk.SetValue(str(team.max_goalkeepers - gk))
        self.panel.remaining_def.SetValue(str(team.max_defenders - df))
        self.panel.remaining_mid.SetValue(str(team.max_midfielders - mf))
        self.panel.remaining_fw.SetValue(str(team.max_forwards - fw))

    # noinspection PyUnusedLocal
    def on_roles(self, event):
        team_name = self.panel.cb_teams.GetValue()
        role = self.panel.rb_roles.GetStringSelection()
        if team_name and role:
            self.fill_players(self.controller.get_team_players(team_name, role))

    # noinspection PyUnusedLocal
    def on_save(self, event):
        if self.is_editor:
            self.update_team(event)
        else:
            self.new_team(event)

    # noinspection PyUnusedLocal
    def new_team(self, event):
        team_name = self.panel.name.GetValue()
        if not team_name:
            wx.MessageBox('You must enter a team name!', 'core info', OK)
        else:
            max_trades = self.panel.trades.GetValue()
            budget = self.panel.budget.GetValue()
            team = self.controller.new_team(team_name, budget, max_trades)
            wx.MessageBox('New team %s created!' % team.name, 'core info', OK)
            self.clear_controls()

    # noinspection PyUnusedLocal
    def update_team(self, event):
        team_name = self.panel.name.GetValue()
        if not team_name:
            wx.MessageBox('Select a Team', 'core info', OK)
        else:
            budget = int(self.panel.budget.GetValue())
            max_t = int(self.panel.trades.GetValue())
            max_g = int(self.panel.remaining_gk.GetValue())
            max_d = int(self.panel.remaining_def.GetValue())
            max_m = int(self.panel.remaining_mid.GetValue())
            max_f = int(self.panel.remaining_fw.GetValue())
            team = self.controller.update_team(team_name, budget, max_t,
                                               max_g, max_d, max_m, max_f)
            wx.MessageBox('Team %s updated' % team.name, 'core info', OK)

    # noinspection PyUnusedLocal
    def delete_team(self, event):
        choice = wx.MessageBox('Deleting Team...are you sure?', 'warning', YN)
        if choice == wx.YES:
            team_name = self.panel.cb_teams.GetValue()
            team = self.controller.get_team(team_name)
            remaining_teams = self.controller.delete_object(team_name)
            self.update_choice_teams(remaining_teams)
            wx.MessageBox('Team %s deleted' % team_name, 'core info', OK)
        else:
            choice.Destroy()
    
    def update_choice_teams(self, teams):
        if not self.panel.cb_teams.GetStringSelection():
            self.panel.cb_teams.Clear()
        self.panel.cb_teams.AppendItems([team.name for team in teams])

    def fill_players(self, players):
        self.panel.player_list.DeleteAllItems()
        for player in players:
            index = self.panel.player_list.InsertStringItem(sys.maxsize,
                                                            str(player.code))
            self.panel.player_list.SetStringItem(index, 1, player.name)
            self.panel.player_list.SetStringItem(index, 2, player.role)
            self.panel.player_list.SetStringItem(index, 3, player.real_team)
            self.panel.player_list.SetStringItem(index, 4, str(player.cost))
            self.panel.player_list.SetStringItem(index, 5,
                                                 str(player.auction_value))

    def clear_controls(self):
        self.panel.name.SetValue('')


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT,
                             size=(200, 200))
        ListCtrlAutoWidthMixin.__init__(self)


class PanelTeam(wx.Panel):
    def __init__(self, parent):
        super(PanelTeam, self).__init__(parent)
        # Attributes
        roles = ['all', 'goalkeeper', 'defender', 'midfielder', 'forward']
        teams = parent.controller.get_teams()
        self.cb_teams = wx.ComboBox(self, -1, "", style=DD, choices=teams)
        self.name = wx.TextCtrl(self)

        self.budget = wx.TextCtrl(self, value=str(500))
        self.trades = wx.TextCtrl(self, value=str(10))
        self.remaining_gk = wx.TextCtrl(self, value=str(3))
        self.remaining_def = wx.TextCtrl(self, value=str(8))
        self.remaining_mid = wx.TextCtrl(self, value=str(8))
        self.remaining_fw = wx.TextCtrl(self, value=str(6))

        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)
        # RADIO BUTTON sizer
        box_roles = wx.BoxSizer(wx.VERTICAL)
        box_roles.Add(self.rb_roles, 0, wx.ALIGN_CENTER_HORIZONTAL, 15)

        self.player_list = AutoWidthListCtrl(self)
        self.player_list.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 50)
        self.player_list.InsertColumn(1, 'name', width=80)
        self.player_list.InsertColumn(2, 'role', width=80)
        self.player_list.InsertColumn(3, 'real team', width=30)
        self.player_list.InsertColumn(4, 'value', width=30)
        self.player_list.InsertColumn(5, 'auction value', width=30)

        # Layout
        text_sizer = wx.FlexGridSizer(rows=8, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Teams:"), 0, ACV)
        text_sizer.Add(self.cb_teams, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Name:"), 0, ACV)
        text_sizer.Add(self.name, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="budget:"), 0, ACV)
        text_sizer.Add(self.budget, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Trades:"), 0, ACV)
        text_sizer.Add(self.trades, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="remaining gk:"), 0, ACV)
        text_sizer.Add(self.remaining_gk, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="remaining def:"), 0, ACV)
        text_sizer.Add(self.remaining_def, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="remaining mf:"), 0, ACV)
        text_sizer.Add(self.remaining_mid, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="remaining fw:"), 0, ACV)
        text_sizer.Add(self.remaining_fw, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)

        # button sizer

        mixin_sizer = wx.BoxSizer(wx.VERTICAL)
        mixin_sizer.Add(wx.StaticText(self, label="Players"), 0, ACV)
        mixin_sizer.Add(self.player_list, 1, wx.EXPAND)

        button_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_save = wx.Button(self, wx.ID_SAVE)
        self.btn_delete = wx.Button(self, wx.ID_DELETE)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_save, 0, ACV)
        button_sizer.Add(self.btn_delete, 0, ACV)
        button_sizer.Add(self.btn_quit, 0, ACV)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_sizer, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(box_roles, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(mixin_sizer, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        self.SetSizer(sizer)
        self.SetBackgroundColour('Pink')
