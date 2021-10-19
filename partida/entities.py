from pony.orm import Database, Required, Optional, Set

db = Database()

class Partida(db.Entity):
    nameGame = Required(str, unique=True)


class Jugador(db.Entity):
    name = Required(str)
    nikcname = Required(str)
    gameName = Required(Partida)


#db.bind('sqlite', 'example.sqlite', create_db=True)  # Conectamos el objeto `db` con la base de datos.

#db.generate_mapping(create_tables=True)  # Generamos las base de datos.

