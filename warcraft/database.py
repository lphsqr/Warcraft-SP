"""Package for the plugin's internal database classes."""

# Python 3 imports
import functools

__all__ = (
    'MySQL',
    'SQLite',
)


class _Database:
    """Wrapper class around SQL database for storing players' data.

    Connects to a database, and creates the tables for ``players``,
    ``heroes``, and ``skills`` if they didn't already exist.

    Provides only methods directly needed by the Warcraft plugin,
    so this is not really a flexible API.
    """

    def __init__(self, *args, **kwargs):
        """Connect to an SQL database and init the tables.

        :param tuple \*args:
            Arguments to forward to the :meth:`_connect` method
        :param dict \*\*kwargs:
            Keyword arguments to forward to the :meth:`_connect` method
        """
        self._connection = self._connect(*args, **kwargs)
        self._connection.execute('''CREATE TABLE IF NOT EXISTS players (
                steamid TEXT PRIMARY KEY NOT NULL,
                active_hero_id TEXT NOT NULL
            )''')
        self._connection.execute('''CREATE TABLE IF NOT EXISTS heroes (
                steamid TEXT NOT NULL,
                class_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                xp INTEGER NOT NULL,
                FOREIGN KEY (steamid) REFERENCES player(steamid),
                PRIMARY KEY (steamid, class_id)
            )''')
        self._connection.execute('''CREATE TABLE IF NOT EXISTS skills (
                steamid TEXT NOT NULL,
                hero_id TEXT NOT NULL,
                class_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                FOREIGN KEY (steamid) REFERENCES players(steamid),
                FOREIGN KEY (hero_id) REFERENCES heroes(class_id),
                PRIMARY KEY (steamid, class_id)
            )''')

    def close(self):
        """Close the connection to the database."""
        self._connection.close()

    def commit(self):
        """Commit changes to the database."""
        self._connection.commit()

    def _connect(self, *args, **kwargs):
        """Connect to the database.

        MySQL and SQLite have different connect functionality, so this
        needs to be overridden by a subclass.
        """
        raise NotImplementedError

    def cursor(self):
        """Return a cursor for the database.

        MySQL and SQLite have different cursor functionality, so this
        needs to be overridden by a subclass.
        """
        raise NotImplementedError

    def get_active_hero_id(self, steamid):
        """Get a player's active hero's :attr:`class_id` (or ``None``).

        :param str steamid:
            SteamID of the player whose active hero to get
        """
        sql = 'SELECT active_hero_id FROM players WHERE steamid=?'
        with self.cursor() as cursor:
            cursor.execute(sql, (steamid,))
            data = cursor.fetchone()
            if data:
                return data[0]
            return None

    def get_heroes_data(self, steamid):
        """Get every hero's data for a player.

        :param str steamid:
            SteamID of the player whose heroes' data to get
        """
        sql = 'SELECT class_id, level, xp FROM heroes WHERE steamid=?'
        with self.cursor() as cursor:
            cursor.execute(sql, (steamid,))
            return cursor.fetchall()

    def get_skills_data(self, steamid, hero_id):
        """Get every skill's data for a hero.

        :param str steamid:
            SteamID of the player who owns the hero
        :param str hero_id:
            ``class_id`` of the hero who owns the skills
        """
        sql = 'SELECT class_id, level FROM skills WHERE steamid=? AND hero_id=?'
        with self.cursor() as cursor:
            cursor.execute(sql, (steamid, hero_id))
            return cursor.fetchall()

    def _save_individual_data(self, query, individual_data):
        """Save individual data into the database.

        Internally calls ``cursor.execute()``.

        :param str query:
            SQL query to execute the data with
        :param iterable individual_data:
            Individual data to insert to the database
        """
        with self.cursor() as cursor:
            cursor.execute(query, individual_data)

    def _save_multiple_data(self, query, multiple_data):
        """Save multiple data into the database.

        Internally calls ``cursor.executemany()``.

        :param str query:
            SQL query to execute the data with
        :param iterable multiple_data:
            Iterable of multiple datas to insert to the database
        """
        with self.cursor() as cursor:
            cursor.executemany(query, multiple_data)

    _PLAYER_QUERY = 'INSERT OR REPLACE INTO players VALUES (?, ?)'
    save_player = functools.partialmethod(_save_individual_data, _PLAYER_QUERY)
    save_players = functools.partialmethod(_save_multiple_data, _PLAYER_QUERY)

    _HERO_QUERY = 'INSERT OR REPLACE INTO heroes VALUES (?, ?, ?, ?)'
    save_hero = functools.partialmethod(_save_individual_data, _HERO_QUERY)
    save_heroes = functools.partialmethod(_save_multiple_data, _HERO_QUERY)

    _SKILL_QUERY = 'INSERT OR REPLACE INTO skills VALUES (?, ?, ?, ?)'
    save_skill = functools.partialmethod(_save_individual_data, _SKILL_QUERY)
    save_skills = functools.partialmethod(_save_multiple_data, _SKILL_QUERY)


class MySQL(_Database):
    """Database class which uses :module:`pymysql` for connecting."""

    def _connect(self, *args, **kwargs):
        import pymysql
        return pymysql.connection(*args, **kwargs)

    def cursor(self):
        return self._connection.cursor


class SQLite(_Database):
    """Databse class which uses :module:`sqlite3` for connecting."""

    def _connect(self, *args, **kwargs):
        import sqlite3
        return sqlite3.connect(*args, **kwargs)

    def cursor(self):
        import contextlib
        return contextlib.closing(self._connection.cursor())
