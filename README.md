# Auction 2.0

Auction 2.0 is a small application to manage a 'Fantaleague' auction.
When the auction is ended it is possible to export the result in a csv file.
Libraries:
django 2.1.3: ORM and db
wxpython 4.0.1: for graphics

## Getting started

Install the packages required in requirements.txt
Launch the main.py file that will create the database:

```
> python main.py
    ...
Migrations for 'auction':
  auction\migrations\0001_initial.py:
    - Create model Player
    - Create model Team
    - Add field team to player
	...
> python manage.py migrate
Operations to perform:
  Apply all migrations: auction
Running migrations:
  Applying auction.0001_initial... OK
```

### Import Players

From Players menu, choose "import players" and import MCCnn.txt file.
MCC files are available in www.bancaldo.wordpress.com and they are Gazzetta compliant.


### Create Teams

Before starting auction, create at least 2 teams from 'Teams' menu.


### Auction

From 'Auction' menu choose 'Start auction'.
Filter the player by Real Team  and Role, then insert the auction value
and the Buyer Team which wins the player auction.

### Changes

From 'Players' and 'Teams' menues is possible to edit and update objects as Team and Player


### Trades

When the auction is ended it is possible to exchange players between teams.
Choose 'Trades' from 'Teams' menu.
It's even possible to add money during an exchange

## Licence

GPL
