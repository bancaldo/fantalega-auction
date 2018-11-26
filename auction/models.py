# noinspection PyUnresolvedReferences
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=32)
    budget = models.IntegerField()
    max_trades = models.IntegerField()
    max_goalkeepers = models.IntegerField()
    max_defenders = models.IntegerField()
    max_midfielders = models.IntegerField()
    max_forwards = models.IntegerField()
    objects = models.Manager()

    def get_max_players(self):
        """
        get_max_players() -> int

        return the max number of players for team (default is 25)
        """
        return sum([self.max_goalkeepers, self.max_defenders,
                    self.max_midfielders, self.max_forwards])

    # noinspection PyUnresolvedReferences
    def get_players_bought(self):
        gk = self.player_set.filter(code__lt=200).count()
        df = self.player_set.filter(code__gte=200).filter(code__lt=500).count()
        mf = self.player_set.filter(code__gte=500).filter(code__lt=800).count()
        fw = self.player_set.filter(code__gte=800).count()
        return gk, df, mf, fw

    # noinspection PyUnresolvedReferences
    def get_players_bought_by_role(self, role):
        return self.player_set.filter(role=role).count()

    # noinspection PyUnresolvedReferences
    def get_players_by_role(self, role):
        return self.player_set.filter(role=role).all()

    def __unicode__(self):
        return self.name


class Player(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=32)
    real_team = models.CharField(max_length=3)
    cost = models.IntegerField()
    auction_value = models.IntegerField(null=True)
    role = models.CharField(max_length=16)
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL)
    objects = models.Manager()

    def __unicode__(self):
        return self.name

    @staticmethod
    def upload_txt(path):
        """
        upload_txt(path)

        This method import players directly from the txt file
        with this format:

           code|name|real_team|f_value|value|cost
        """
        with open(path) as data:
            for record in data:
                code, name, real_team, f_value, value, cost = \
                    record.strip().split("|")
                player = Player.objects.filter(code=int(code.strip())).first()
                if player:
                    player.name = name
                    player.real_team = real_team
                    player.cost = int(cost.strip())
                    player.save()
                    print("   INFO: %s updated!" % name)
                else:
                    Player.objects.create(code=int(code), name=name.upper(),
                                          real_team=real_team.upper(),
                                          cost=int(cost))
                    print("   INFO: New player %s created" % name)
            print("   INFO: Player file uploading done!")
