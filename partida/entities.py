from pony.orm import *

db = Database()
set_sql_debug(True)

class Game(db.Entity):
    ID = PrimaryKey(int, auto=True)
    name = Required(str)
    started = Required(bool, default=False)
    players = Set('Player')



class Player(db.Entity):
    name = Required(str)
    nikcname = Required(str)
    gameName = Required(Game)

@db_session
def getGame():
    return select(g for g in Game)[:]

@db_session
def getGamebyName(name):
    return select(g for g in Game if g.name == name)[:]

@db_session
def addGame(name):
    Game(name = name)
    commit()


# db.bind('sqlite', 'example.sqlite', create_db=True)  # Conectamos el objeto `db` con la base de datos.

# db.generate_mapping(create_tables=True)  # Generamos las base de datos.

# addGame("Partida1")
# a = getGamebyName("Partida1")
# print(a[0].name)
