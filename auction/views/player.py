import wx
import sys
import platform
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from auction.views.styles import OK, ACV, ACH


class ViewPlayer(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        self.parent = parent
        self.is_editor = is_editor
        super(ViewPlayer, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelPlayer(parent=self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        size = (350, 500) if platform.system() == 'Linux' else (350, 450)
        self.SetSize(size)

        self.panel.btn_delete.Disable()
        if not self.is_editor:
            self.panel.cb_players.Disable()

        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_BUTTON, self.delete_player, self.panel.btn_delete)
        self.Bind(wx.EVT_COMBOBOX, self.on_cb_players, self.panel.cb_players)
        self.Bind(wx.EVT_RADIOBOX, self.on_rb_roles, self.panel.rb_roles)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_save(self, event):
        if self.is_editor:
            self.update_player(event)
        else:
            self.new_player(event)

    # noinspection PyUnusedLocal
    def on_rb_roles(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        players = self.controller.get_players(role=role)
        self.panel.cb_players.Clear()
        self.panel.cb_players.AppendItems(players)

    # noinspection PyUnusedLocal
    def on_cb_players(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        player_name = self.panel.cb_players.GetStringSelection()
        player = self.controller.get_player_by_name(player_name)
        self.controller.set_temporary_object(player)
        self.panel.name.SetValue(player.name)
        self.panel.code.SetValue(str(player.code))
        self.panel.real_team.SetValue(player.real_team)
        self.panel.value.SetValue(str(player.cost))
        self.panel.auction_value.SetValue(str(player.auction_value))
        if not player.auction_value:
            self.panel.auction_value.SetValue(str(0))
        self.panel.cb_teams.Clear()
        teams = self.controller.get_teams()
        self.panel.cb_teams.AppendItems(teams)
        if player.team:
            self.panel.cb_teams.SetValue(player.team.name)

    # noinspection PyUnusedLocal
    def new_player(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        code = int(self.panel.code.GetValue())
        player_name = self.panel.name.GetValue()
        real_team = self.panel.real_team.GetValue()
        value = int(self.panel.value.GetValue())
        auction_value = int(self.panel.auction_value.GetValue())
        team_name = self.panel.cb_teams.GetStringSelection()

        self.controller.new_player(code, player_name, real_team, value,
                                   auction_value, team_name)
        wx.MessageBox('New Player [%s] %s saved!' % (code, player_name),
                      'core info', OK)
        self.clear_fields()

    def clear_fields(self):
        for w in [w for w in self.panel.GetChildren()
                  if isinstance(w, wx.TextCtrl)]:
            w.SetValue('')

    # noinspection PyUnusedLocal
    def update_player(self, event):
        old_auction_value = self.controller.get_temporary_object().auction_value
        imp = self.controller.get_temporary_object()
        new_team = self.panel.cb_teams.GetValue()
        role = self.panel.rb_roles.GetStringSelection()
        code = int(self.panel.code.GetValue())
        player_name = self.panel.name.GetValue()
        real_team = self.panel.real_team.GetValue()
        value = int(self.panel.value.GetValue())

        try:
            auction_value = int(self.panel.auction_value.GetValue())
        except ValueError:
            auction_value = 0

        try:
            if imp.team.name == new_team:
                if old_auction_value != auction_value:
                    if old_auction_value is None:
                        old_auction_value = 0
                    difference = old_auction_value - auction_value
                    self.controller.update_budget(new_team, difference)
            else:
                if not new_team:
                    print("[INFO] %s team --> None" % player_name)
                    print("[INFO] %s budget --> +%s" % (imp.team.name,
                                                        auction_value))
                    self.controller.update_budget(imp.team.name, auction_value)
                    new_team = None
                else:
                    print("[INFO] %s team %s --> %s" % (player_name,
                                                        imp.team.name,
                                                        new_team))
                    # update old team budget
                    self.controller.update_budget(imp.team.name, auction_value)
                    # update new team budget
                    self.controller.update_budget(new_team, -auction_value)

            self.controller.update_player(code, player_name, real_team,
                                          value, auction_value, role, new_team)
        except AttributeError:
            if not new_team:
                print("[INFO] no-team player %s updated!")
            else:
                print("[INFO] %s team: None --> %s" % (player_name, new_team))

            self.controller.update_player(code, player_name, real_team,
                                          value, auction_value, role, new_team)

        wx.MessageBox('Player %s updated!' % player_name, 'core info', OK)
        self.clear_fields()
        self.panel.cb_players.Clear()
        self.panel.cb_players.AppendItems(
            self.controller.get_players(role=role))

    # noinspection PyUnusedLocal
    def delete_player(self, event):
        choice = wx.MessageBox('Deleting League...are you sure?', 'warning',
                               wx.YES_NO | wx.ICON_WARNING)
        role = self.panel.rb_roles.GetStringSelection()
        if choice == wx.YES:
            player_name = self.panel.cb_players.GetStringSelection()
            player = self.controller.get_player_by_name(player_name)
            self.controller.delete_object(player)
            players = self.controller.get_players(role=role)
            self.fill_combobox(self.panel.cb_players, players)
            wx.MessageBox("%s deleted!" % player, 'core info', OK)
            self.parent.check_menu_player()
        else:
            choice.Destroy()

    @staticmethod
    def fill_combobox(combobox, items):
        combobox.Clear()
        combobox.AppendItems([item.name for item in items])


class PanelPlayer(wx.Panel):
    def __init__(self, parent):
        super(PanelPlayer, self).__init__(parent)
        # Attributes
        roles = ['goalkeeper', 'defender', 'midfielder', 'forward']
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)

        players = parent.controller.get_players(role='goalkeeper')
        self.cb_players = wx.ComboBox(self, -1, "", choices=players,
                                      style=wx.CB_DROPDOWN)
        self.code = wx.TextCtrl(self)
        self.name = wx.TextCtrl(self)
        self.real_team = wx.TextCtrl(self)
        self.value = wx.TextCtrl(self)
        self.auction_value = wx.TextCtrl(self)
        self.cb_teams = wx.ComboBox(self, -1, "", style=wx.CB_DROPDOWN)

        # Layout
        box_roles = wx.BoxSizer(wx.VERTICAL)
        box_roles.Add(self.rb_roles, 0, wx.ALIGN_CENTER_HORIZONTAL, 15)

        text_sizer = wx.FlexGridSizer(rows=7, cols=2, hgap=5, vgap=5)

        text_sizer.Add(wx.StaticText(self, label="Player:"), 0, ACV)
        text_sizer.Add(self.cb_players, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Code:"), 0, ACV)
        text_sizer.Add(self.code, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Name:"), 0, ACV)
        text_sizer.Add(self.name, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Real team:"), 0, ACV)
        text_sizer.Add(self.real_team, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Value:"), 0, ACV)
        text_sizer.Add(self.value, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Auction Value:"), 0, ACV)
        text_sizer.Add(self.auction_value, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Team:"), 0, ACV)
        text_sizer.Add(self.cb_teams, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)

        button_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_save = wx.Button(self, wx.ID_SAVE)
        self.btn_delete = wx.Button(self, wx.ID_DELETE)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_save, 0, wx.ALIGN_CENTER_VERTICAL)
        button_sizer.Add(self.btn_delete, 0, wx.ALIGN_CENTER_VERTICAL)
        button_sizer.Add(self.btn_quit, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(text_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetBackgroundColour('Pink')
        self.SetSizer(sizer)


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class ViewPlayerSummary(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewPlayerSummary, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        players = self.controller.get_players()
        self.panel = PanelPlayerSummary(parent=self)
        size = (900, 500) if platform.system() == 'Linux' else (800, 500)
        self.SetSize(size)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list,
                  self.panel.player_list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.player_list)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_RADIOBOX, self.on_roles)
        self.fill_player_list(players)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        self.panel.player_list.DeleteAllItems()
        role = self.panel.rb_roles.GetStringSelection()
        players = self.controller.get_players(role=role)
        self.fill_player_list(players)

    # noinspection PyUnusedLocal
    def on_list(self, event):
        item_id = event.GetIndex() if wx.version().startswith('4') else \
            event.m_itemIndex
        code = self.panel.player_list.GetItemText(item_id)
        view_edit = ViewPlayer(self.parent, "Edit Player", is_editor=True)
        view_edit.panel.code.ChangeValue(code)
        player = self.controller.get_player_by_code(code)
        self.controller.set_temporary_object(player)
        if player:
            view_edit.panel.cb_players.Disable()
            view_edit.panel.code.ChangeValue(str(player.code))
            view_edit.panel.name.ChangeValue(str(player.name))
            view_edit.panel.real_team.ChangeValue(str(player.real_team))
            view_edit.panel.value.ChangeValue(str(player.cost))
            view_edit.panel.auction_value.ChangeValue(str(player.auction_value))
            view_edit.panel.cb_teams.ChangeValue(str(player.team))
            view_edit.panel.btn_delete.Enable()
            view_edit.SetWindowStyle(wx.STAY_ON_TOP)
        else:
            wx.MessageBox('recently modified Object: please click REFRESH',
                          wx.OK | wx.ICON_EXCLAMATION)

    def on_list_column(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        id_column = event.GetColumn()
        players = self.controller.get_sorted_players(id_column, role)
        self.fill_player_list(players)

    # noinspection PyUnusedLocal
    def on_roles(self, event):
        role = self.panel.rb_roles.GetStringSelection()
        players = self.controller.get_players(role=role)
        self.fill_player_list(players)

    def fill_player_list(self, players):
        self.panel.player_list.DeleteAllItems()
        insert_item = self.panel.player_list.InsertStringItem
        set_item = self.panel.player_list.SetStringItem
        if wx.version().startswith('4'):
            insert_item = self.panel.player_list.InsertItem
            set_item = self.panel.player_list.SetItem

        for player_name in players:
            player = self.controller.get_player_by_name(player_name)
            index = insert_item(sys.maxsize, str(player.code))
            set_item(index, 1, player.name)
            set_item(index, 2, player.real_team)
            set_item(index, 3, str(player.cost))
            set_item(index, 4, str(player.auction_value))
            if player.team:
                set_item(index, 5, player.team.name)


class PanelPlayerSummary(wx.Panel):
    def __init__(self, parent):
        super(PanelPlayerSummary, self).__init__(parent=parent)
        roles = ['goalkeeper', 'defender', 'midfielder', 'forward']
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.player_list = AutoWidthListCtrl(self)
        self.player_list.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 50)
        self.player_list.InsertColumn(1, 'name', width=150)
        self.player_list.InsertColumn(2, 'real team', width=50)
        self.player_list.InsertColumn(3, 'value', width=50)
        self.player_list.InsertColumn(4, 'auction value', width=50)
        self.player_list.InsertColumn(5, 'team', width=100)

        # RADIO BUTTON sizer
        box_roles = wx.BoxSizer(wx.VERTICAL)
        box_roles.Add(self.rb_roles, 0, ACH, 15)
        # BUTTONS sizer
        btn_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)
        player_list_box = wx.BoxSizer(wx.HORIZONTAL)
        player_list_box.Add(self.player_list, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(player_list_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
