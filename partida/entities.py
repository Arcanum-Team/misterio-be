from pony.orm import *
from uuid import UUID

db = Database()
set_sql_debug(True)

class Game(db.Entity):
    name = Required(str)
    started = Required(bool, default=False)
    players = Set('Player')


class Player(db.Entity):
    name = Required(str)
    nikcname = Required(str)
    gameID = Required(Game)
    isHost= Required(bool)

# Game querys
@db_session
def getGames():
    return select(g for g in Game)[:]

@db_session
def getGamebyName(name):
    return select(g for g in Game if g.name == name)[:]

@db_session
def addGame(name):
    Game(name = name)
    commit()

@db_session
def startGame(name, host_id):
    game = getGamebyName(name)[0]
    game.started = True
    player = getPlayerbyID(host_id)
    player[0].gameID = game.id

# Player querys
@db_session
def getPlayerbyID(id):
    return select(p for p in Player if p.id == id)[:]

@db_session
def addPlayer(name, nikcname, gameName):
    game = getGamebyName(gameName)[0]
    p = Player(name = name, nikcname = nikcname, gameID = game.id)
    commit()
    return p.id


db.bind('sqlite', 'example.sqlite', create_db=True)  # Conectamos el objeto `db` con la base de datos.

db.generate_mapping(create_tables=True)  # Generamos las base de datos.

""" addGame("Partida1")
id = addPlayer("juan", "juancito", "Partida1")
a = getGamebyName("Partida1") 
print(a[0].name, a[0].started, id)
show(Player) """
