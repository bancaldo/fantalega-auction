# noinspection PyUnresolvedReferences
from auction.models import Player, Team


class Model:
    def __init__(self):
        super(Model, self).__init__()
        self.temporary_object = None
        self.bulk_players_to_update = []
        self.bulk_players_to_create = []

    def set_temporary_object(self, obj):
        self.temporary_object = obj

    def get_temporary_object(self):
        return self.temporary_object

    @staticmethod
    def delete_object(obj):
        obj.delete()

    # TEAM methods -------------------------------------------------------------
    @staticmethod
    def get_team(name):
        return Team.objects.filter(name=name.upper()).first()

    @staticmethod
    def get_teams():
        return Team.objects.all()

    @staticmethod
    def new_team(team_name, budget, max_t, max_g=3, max_d=8, max_m=8, max_f=6):
        team = Team.objects.create(name=team_name.upper(), budget=budget,
                                   max_trades=max_t, max_goalkeepers=max_g,
                                   max_defenders=max_d, max_midfielders=max_m,
                                   max_forwards=max_f)
        team.save()
        return team

    def update_team(self, team_name, budget, max_t, max_g, max_d, max_m, max_f):
        team = self.get_team(team_name)
        if not team:
            team = self.get_temporary_object()
        team.name = team_name
        team.budget = budget
        team.max_trades = max_t
        team.max_goalkeepers = max_g
        team.max_defenders = max_d
        team.max_midfielders = max_m
        team.max_forwards = max_f
        team.save()
        return team

    def update_budget(self, team_name, difference):
        team = self.get_team(team_name)
        old_budget = team.budget
        team.budget += int(difference)
        print("   INFO:: %s budget updated: %s --> %s" % (team_name, old_budget,
                                                          team.budget))
        team.save()

    @staticmethod
    def get_teams_count():
        return Team.objects.count()

    def discard_player(self, player_code):
        player = self.get_player_by_code(int(player_code))
        team = player.team
        auction_value = player.auction_value
        if not auction_value:
            auction_value = 0
        team.budget += auction_value
        team.save()
        print("   INFO: Team %s budget: +%s" % (team.name, auction_value))
        player.team = None
        player.auction_value = None
        print("   INFO: Player %s updated" % player.name)
        player.save()

    # PLAYER methods -----------------------------------------------------------
    def new_player(self, player_code, player_name, real_team, cost):
        role = self.get_role_by_code(player_code)
        return Player.objects.create(code=int(player_code), cost=cost,
                                     name=player_name.upper(),
                                     real_team=real_team, role=role)

    def add_new_player_to_bulk(self, player_code, player_name, real_team, cost):
        name = u'%s' % player_name.upper()
        role = self.get_role_by_code(player_code)
        player = Player(code=int(player_code), cost=cost,
                        name=name, real_team=real_team, role=role)
        self.bulk_players_to_create.append(player)

    def import_all_players(self):
        Player.objects.bulk_create(self.bulk_players_to_create)

    def clear_bulk_players(self):
        self.bulk_players_to_create = []

    @staticmethod
    def get_players_count():
        return Player.objects.count()

    @staticmethod
    def get_player_by_name(player_name):
        return Player.objects.filter(name=player_name.upper()).first()

    @staticmethod
    def get_player_by_code(player_code):
        return Player.objects.filter(code=int(player_code)).first()

    def buy_player(self, player_name, cost, team_name):
        team = self.get_team(team_name)
        player = self.get_player_by_name(player_name)
        in_team = [p for p in team.player_set.all() if p.role == player.role]

        if player.team == team:
            old_cost = int(player.auction_value)
            diff_cost = old_cost - int(cost)
            team.budget += diff_cost
            player.auction_value = int(cost)
            player.save()
            print("[WARNING] Player previously bought, updating...")
            print("[INFO} %s values upgraded!" % player.name)
        else:
            if player.role.lower() == 'goalkeeper':
                max_p = team.max_goalkeepers
            elif player.role.lower() == 'defender':
                max_p = team.max_defenders
            elif player.role.lower() == 'midfielder':
                max_p = team.max_midfielders
            else:
                max_p = team.max_forwards

            if len(in_team) < max_p:
                bought = len(team.player_set.all())
                max_players = team.get_max_players()
                remaining = max_players - bought
                cash = int(team.budget)
                if (cash - remaining) > 0:
                    if player in team.player_set.all():
                        print("[ERROR] Player previously bought")
                    elif player.team:
                        print("[ERROR] Player already bought by another team")
                    else:
                        team.player_set.add(player)
                        team.budget -= int(cost)
                        team.save()
                        player.auction_value = cost
                        player.save()
                        print("   INFO: %s [%s] %s saved!" % (player.name,
                                                              cost, team.name))
                else:
                    print("[ERROR] Not enough money to complete team")
            else:
                print("[ERROR] players limit reached.")

    @staticmethod
    def get_players_ordered_by_filter(filter_name, role):
        return Player.objects.filter(role=role).order_by(filter_name)

    def sell_player(self, player_name):
        player = self.get_player_by_name(player_name)
        team = player.team
        team.player_set.remove(player)
        team.save()
        return team.player_set.all()

    @staticmethod
    def delete_players():
        Player.objects.all().delete()

    @staticmethod
    def get_players(role=None, real_team=None):
        if role and not real_team:
            return Player.objects.filter(role=role).all()
        elif real_team and not role:
            return Player.objects.filter(real_team=real_team).all()
        elif role and real_team:
            return Player.objects.filter(role=role, real_team=real_team).all()
        else:
            return Player.objects.all()

    @staticmethod
    def get_free_players(role=None):
        players = Player.objects.filter(team=None)
        if role:
            return players.filter(role=role).all()
        return players

    def get_team_players(self, team_name, role):
        team = self.get_team(team_name)
        if role.lower() == 'all':
            return Player.objects.filter(team=team).all()
        return Player.objects.filter(team=team, role=role).all()

    def employed(self):
        return [p for p in self.get_players() if p.team is not None]

    def available_players(self, role=None, prefix=''):
        free = [g for g in self.get_players() if g.team is None]
        if role is None and prefix == '':
            available = free
        elif role and prefix == '':
            available = [p for p in free if p.role == role.strip()]
        elif prefix and role is None:
            available = [p for p in free if p.name.startswith(
                prefix.strip().upper())]
        else:
            available = [p for p in free if p.role == role.strip() and
                         p.name.startswith(prefix.upper().strip())]
        return available

    def do_transfer(self, player_name, team_name):
        player = self.get_player_by_name(player_name)
        team = self.get_team(team_name)
        team.budget -= player.cost
        team.max_trades -= 1
        player.team = team
        team.save()
        player.save()

    @staticmethod
    def get_real_teams():
        return [player['real_team'] for player in
                Player.objects.order_by('real_team').values(
                    'real_team').distinct()]

    def update_player(self, code, player_name, real_team, cost, auction_value,
                      role, team_name):
        team = self.get_team(team_name)
        player = self.get_player_by_name(player_name)
        if not player:
            player = self.get_temporary_object()
        player.code = code
        player.name = player_name.strip().upper()
        player.real_team = real_team.strip().upper()
        player.cost = int(cost)
        player.auction_value = int(auction_value)
        player.role = role.strip().lower()
        player.team = team
        if not team:
            print("[WARNING] Player removed from previous team")
        player.save()
        print("   INFO: Player %s updated!" % player_name)
        return player

    def update_import_player(self, player_code, player_name, real_team, cost):
        player = self.get_player_by_code(player_code)
        player.name = player_name.strip().upper()
        player.real_team = real_team.strip().upper()
        player.cost = int(cost)
        player.role = self.get_role_by_code(player_code)
        player.save()
        return player

    @staticmethod
    def get_role_by_code(code):
        if int(code) < 200:
            role = 'goalkeeper'
        elif 200 <= int(code) < 500:
            role = 'defender'
        elif 500 <= int(code) < 800:
            role = 'midfielder'
        else:
            role = 'forward'
        return role

    def change_budgets(self, left_team_name, left_extra_budget,
                       right_team_name, right_extra_budget):
        left_team = self.get_team(left_team_name)
        old_left_budget = left_team.budget
        left_team.budget += (int(right_extra_budget) - int(left_extra_budget))
        left_team.save()
        print("   INFO: team %s budget: %s --> %s" % (left_team,
                                                      old_left_budget,
                                                      left_team.budget))
        right_team = self.get_team(right_team_name)
        old_right_budget = right_team.budget
        right_team.budget += (int(left_extra_budget) - int(right_extra_budget))
        right_team.save()
        print("   INFO: team %s budget: %s --> %s" % (right_team,
                                                      old_right_budget,
                                                      right_team.budget))

    def split_players(self, left_team_name, left_player_name,
                      right_team_name, right_player_name):
        left_player = self.get_player_by_name(left_player_name)
        left_team = self.get_team(left_team_name)
        right_player = self.get_player_by_name(right_player_name)
        right_team = self.get_team(right_team_name)

        left_player.team = right_team
        right_player.team = left_team
        left_player.save()
        right_player.save()
        left_team.save()
        right_team.save()
