import wx
import platform
from auction.views.styles import OK, ACV


class ViewTrade(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewTrade, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelTrade(parent=self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        size = (400, 500) if platform.system() == 'Linux' else (300, 425)
        self.SetSize(size)

        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_RADIOBOX, self.on_rb_roles, self.panel.rb_roles)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_COMBOBOX, self.on_left_team, self.panel.cb_left_teams)
        self.Bind(wx.EVT_COMBOBOX, self.on_right_team,
                  self.panel.cb_right_teams)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_rb_roles(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        left_team_name = self.panel.cb_left_teams.GetValue()
        right_team_name = self.panel.cb_right_teams.GetValue()
        if left_team_name:
            left_team = self.controller.get_team(left_team_name)
            left_players = left_team.get_players_by_role(role)
            self.panel.cb_left_players.Clear()
            self.panel.cb_left_players.AppendItems([p.name
                                                    for p in left_players])
        if right_team_name:
            right_team = self.controller.get_team(right_team_name)
            right_players = right_team.get_players_by_role(role)
            self.panel.cb_right_players.Clear()
            self.panel.cb_right_players.AppendItems([p.name
                                                     for p in right_players])

    # noinspection PyUnusedLocal
    def on_left_team(self, event):
        team_name = self.panel.cb_left_teams.GetStringSelection()
        team = self.controller.get_team(team_name)
        self.panel.left_budget.SetValue(str(team.budget))
        role = self.panel.rb_roles.GetStringSelection()
        players = self.controller.get_team_players(team_name, role)
        print(players)
        self.panel.cb_left_players.Clear()
        self.panel.cb_left_players.AppendItems([p.name for p in players])

    # noinspection PyUnusedLocal
    def on_right_team(self, event):
        team_name = self.panel.cb_right_teams.GetStringSelection()
        team = self.controller.get_team(team_name)
        self.panel.right_budget.SetValue(str(team.budget))
        role = self.panel.rb_roles.GetStringSelection()
        players = team.get_players_by_role(role)
        self.panel.cb_right_players.Clear()
        self.panel.cb_right_players.AppendItems([p.name for p in players])

    def clear_fields(self):
        for w in [w for w in self.panel.GetChildren()
                  if isinstance(w, wx.TextCtrl)]:
            w.SetValue('')

    def clear_comboboxes(self):
        for w in [w for w in self.panel.GetChildren()
                  if isinstance(w, wx.ComboBox)]:
            w.ChangeValue('')
            w.Clear()

    # noinspection PyUnusedLocal
    def on_save(self, event):
        left_team_name = self.panel.cb_left_teams.GetStringSelection()
        left_budget = self.panel.left_budget.GetValue()
        left_extra_budget = self.panel.left_extra_budget.GetValue()
        left_player_name = self.panel.cb_left_players.GetStringSelection()

        right_team_name = self.panel.cb_right_teams.GetStringSelection()
        right_budget = self.panel.right_budget.GetValue()
        right_extra_budget = self.panel.right_extra_budget.GetValue()
        right_player_name = self.panel.cb_right_players.GetStringSelection()

        if (int(left_extra_budget) > int(left_budget)) or \
           (int(right_extra_budget) > int(right_budget)):
            wx.MessageBox('Not enough money to add on trade operation!',
                          'core info', OK)
        else:
            self.controller.change_budgets(left_team_name, left_extra_budget,
                                           right_team_name, right_extra_budget)

            self.controller.split_players(left_team_name, left_player_name,
                                          right_team_name, right_player_name)
            wx.MessageBox('Trade operation done!', 'core info', OK)
            self.clear_fields()
            self.clear_comboboxes()
            teams = self.controller.get_teams()
            self.panel.cb_left_teams.AppendItems(teams)
            self.panel.cb_right_teams.AppendItems(teams)

    @staticmethod
    def fill_combobox(combobox, items):
        combobox.Clear()
        combobox.AppendItems([item.name for item in items])


class PanelTrade(wx.Panel):
    def __init__(self, parent):
        super(PanelTrade, self).__init__(parent)
        # Attributes
        roles = ['goalkeeper', 'defender', 'midfielder', 'forward']
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)
        # left team widgets
        teams = parent.controller.get_teams()
        self.cb_left_teams = wx.ComboBox(self, -1, "", style=wx.CB_DROPDOWN,
                                         choices=teams)
        self.cb_left_players = wx.ComboBox(self, -1, "", style=wx.CB_DROPDOWN)
        self.left_budget = wx.TextCtrl(self)
        self.left_extra_budget = wx.TextCtrl(self, value='0')

        # right team widgets
        self.cb_right_teams = wx.ComboBox(self, -1, "", style=wx.CB_DROPDOWN,
                                          choices=teams)
        self.cb_right_players = wx.ComboBox(self, -1, "", style=wx.CB_DROPDOWN)
        self.right_budget = wx.TextCtrl(self)
        self.right_extra_budget = wx.TextCtrl(self, value='0')

        # radio button sizer
        box_roles = wx.BoxSizer(wx.VERTICAL)
        box_roles.Add(self.rb_roles, 0, wx.ALIGN_CENTER_HORIZONTAL, 15)

        # left team sizer
        left_team_sizer = wx.FlexGridSizer(rows=8, cols=1, hgap=5, vgap=5)
        left_team_sizer.Add(wx.StaticText(self, label="Team:"), 0, ACV)
        left_team_sizer.Add(self.cb_left_teams, 0, wx.EXPAND)
        left_team_sizer.Add(wx.StaticText(self, label="Player:"), 0, ACV)
        left_team_sizer.Add(self.cb_left_players, 0, wx.EXPAND)
        left_team_sizer.Add(wx.StaticText(self, label="budget:"), 0, ACV)
        left_team_sizer.Add(self.left_budget, 0, wx.EXPAND)
        left_team_sizer.Add(wx.StaticText(self, label="Extra budget:"), 0, ACV)
        left_team_sizer.Add(self.left_extra_budget, 0, wx.EXPAND)

        # right team sizer
        right_team_sizer = wx.FlexGridSizer(rows=8, cols=1, hgap=5, vgap=5)
        right_team_sizer.Add(wx.StaticText(self, label="Team:"), 0, ACV)
        right_team_sizer.Add(self.cb_right_teams, 0, wx.EXPAND)
        right_team_sizer.Add(wx.StaticText(self, label="Player:"), 0, ACV)
        right_team_sizer.Add(self.cb_right_players, 0, wx.EXPAND)
        right_team_sizer.Add(wx.StaticText(self, label="budget:"), 0, ACV)
        right_team_sizer.Add(self.right_budget, 0, wx.EXPAND)
        right_team_sizer.Add(wx.StaticText(self, label="Extra budget:"), 0, ACV)
        right_team_sizer.Add(self.right_extra_budget, 0, wx.EXPAND)

        # horiontal teams sizer
        team_sizer = wx.BoxSizer(wx.HORIZONTAL)
        team_sizer.Add(left_team_sizer, 0, wx.EXPAND | wx.ALL, 5)
        team_sizer.Add(right_team_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # button sizer
        button_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_save = wx.Button(self, wx.ID_SAVE)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_save, 0, wx.ALIGN_CENTER_VERTICAL)
        button_sizer.Add(self.btn_quit, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(team_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetBackgroundColour('Pink')
        self.SetSizer(sizer)
