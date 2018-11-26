# noinspection PyUnresolvedReferences
from auction.models import Team, Player
# noinspection PyUnresolvedReferences
from django.contrib import messages
# noinspection PyUnresolvedReferences
from django.utils import timezone
from auction.views.core import Core
from auction.model import Model


class Controller:
    def __init__(self):
        super(Controller, self).__init__()
        self.model = Model()
        self.view = Core(parent=None, controller=self, title='Auction 2.0')
        self.view.Show()

    def set_temporary_object(self, obj):
        self.model.set_temporary_object(obj)

    def get_temporary_object(self):
        return self.model.get_temporary_object()

    def delete_object(self, obj):
        return self.model.delete_object(obj)

    # TEAM methods -------------------------------------------------------------
    def new_team(self, name, budget, trades):
        return self.model.new_team(name, budget, trades)

    def get_teams(self):
        return [team.name for team in self.model.get_teams()]

    def update_team(self, team_name, budget, max_t, max_g, max_d, max_m, max_f):
        self.model.update_team(team_name, budget, max_t, max_g, max_d,
                               max_m, max_f)
        print("   INFO: Team %s updated" % team_name)
        return self.model.update_team(team_name, budget, max_t, max_g, max_d,
                                      max_m, max_f)

    # PLAYER methods -----------------------------------------------------------
    def get_free_players(self, role=None):
        return self.model.get_free_players(role)

    def get_players(self, role=None, real_team=None):
        return [p.name for p in self.model.get_players(role, real_team)]

    def get_sorted_players(self, id_c, role):
        columns = {0: 'code', 1: 'name', 2: 'real_team', 3: '-cost',
                   4: '-auction_value', 5: 'team'}
        players = self.model.get_players_ordered_by_filter(columns.get(id_c),
                                                           role)
        return [player.name for player in players]

    def get_player_by_name(self, player_name):
        return self.model.get_player_by_name(player_name)

    def get_players_count(self):
        return self.model.get_players_count()

    def get_player_by_code(self, player_code):
        return self.model.get_player_by_code(player_code)

    def available_players(self, role=None, prefix=''):
        players = self.model.available_players(role=role, prefix=prefix)
        return ['%s > %s' % (g.name, g.role.lower()) for g in players]

    def get_player_values(self, name):
        p = self.model.get_player_by_name(name)
        if p:
            return p.code, p.name, p.real_team, p.value, p.auction_value, p.role

    def update_budget(self, team_name, difference):
        self.model.update_budget(team_name, difference)

    def get_team(self, name):
        return self.model.get_team(name)

    def get_teams_count(self):
        return self.model.get_teams_count()

    def get_team_values(self, name):
        team = self.model.get_team(name)
        if team:
            values = (team.name, team.allenatore, team.budget,
                      team.op_mercato)
            return values

    def get_team_players(self, team_name, role):
            return self.model.get_team_players(team_name, role)

    def get_real_teams(self):
        return self.model.get_real_teams()

    def do_transfer(self, player_name, team_name):
        self.model.do_transfer(player_name, team_name)
        print("   INFO: Transfer %s --> %s" % (player_name, team_name))

    def discard_player(self, player_code):
        self.model.discard_player(player_code)

    # PLAYER method ------------------------------------------------------------
    def update_player(self, code, player_name, real_team, cost, auction_value,
                      role, team_name):
        return self.model.update_player(code, player_name, real_team, cost,
                                        auction_value, role, team_name)

    def sell_player(self, player_name):
        return ['%s > %s' % (player.name, player.role.lower())
                for player in self.model.sell_player(player_name)]

    def buy_player(self, player_name, cost, team):
        return self.model.buy_player(player_name, cost, team)

    def set_role(self, role):
        self.model.role = role

    def delete_players(self):
        self.model.clear_bulk_players()
        self.model.delete_players()

    def import_player_bulk(self, record):
        player_code, player_name, real_team, fanta_value, net_value, cost = \
            record.split('|')
        self.model.add_new_player_to_bulk(player_code, player_name,
                                          real_team, cost)

    def commit_all_players(self):
        self.model.import_all_players()

    def import_player(self, record):
        player_code, player_name, real_team, fanta_value, net_value, cost = \
            record.split('|')
        player = self.model.get_player_by_code(player_code)
        if not player:
            p = self.model.new_player(player_code, player_name, real_team, cost)
            print("   INFO: new player <%s> created!" % player_name)
        else:
            p = self.model.update_import_player(player_code, player_name,
                                                real_team, cost)
            print("   INFO: player <%s> updated!" % player_name)
        return p

    def change_budgets(self, left_team_name, left_extra_budget,
                       right_team_name, right_extra_budget):
        self.model.change_budgets(left_team_name, left_extra_budget,
                                  right_team_name, right_extra_budget)

    def split_players(self, left_team_name, left_player_name,
                      right_team_name, right_player_name):
        self.model.split_players(left_team_name, left_player_name,
                                 right_team_name, right_player_name)
        print("   INFO: player %s team: %s --> %s" % (left_player_name,
                                                      left_team_name,
                                                      right_team_name))
        print("   INFO: player %s team: %s --> %s" % (right_player_name,
                                                      right_team_name,
                                                      left_team_name))

    def export_to_csv(self):
        print("   INFO: Exporting teams to 'auction.csv' file...")
        teams = self.get_teams()
        if teams:
            max_p = self.get_team(teams[0]).get_max_players()
            header = "%s;;" * len(teams)
            with open('auction.csv', 'w') as output:
                # write header
                output.write("%s\n" % (header % tuple(teams)))
                for team_name in teams:
                    team = self.get_team(team_name)
                    if sum(team.get_players_bought()) != team.get_max_players():
                        print("--ERROR: Missing Player in team %s" % team.name)
                        self.view.show_message("Missing Player in team %s"
                                               % team.name)
                index = 0
                line = "%s;%s;" * len(teams)
                while index < max_p:
                    players = []
                    for team_name in teams:
                        team = self.get_team(team_name)
                        try:
                            players.append(team.player_set.all()[index])
                        except IndexError:
                            break
                    values = [(p.name, p.auction_value) for p in players]
                    mixed = []
                    for t in values:
                        for item in t:
                            mixed.append(item)
                    index += 1
                    try:
                        output.write("%s\n" % (line % tuple(mixed)))
                    except TypeError:
                        output.write(";;;;;;;;;;\n")

                footer = "budget;%s;" * len(teams)
                output.write(footer % tuple([t.budget for t
                                             in [self.get_team(tn)
                                                 for tn in teams]]))
                print("   INFO: Auction exported to auction.csv file")
                self.view.show_message("Auction exported to auction.csv file")
        else:
            print("WARNING: No Teams in db, please create them")
            self.view.show_message("No Teams in db, please create them")
