# Python 3 imports
import collections

# SQLAlchemy imports
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

# Custom Source.Python imports
import easyplayer

# Warcraft imports
import warcraft.database
from warcraft.entities import Hero

__all__ = (
    'Player',
)


class Player(easyplayer.Player, warcraft.database.Base):
    """Player class with support for managing Warcraft heroes.

    Each player has an ordered dictionary of his heroes in the format
    of ``{hero.class_id: hero}`` stored into :attr:`heroes` attribute.
    The player also has a :attr:`hero` attribute to store the hero
    he's currently playing with.
    """
    __tablename__ = 'player'
    id = Column(String(21), primary_key=True)
    heroes = relationship('Hero', collection_class=attribute_mapped_collection('id'))
    _active_hero_id = Column(Integer, ForeignKey('hero.id'))

    def __init__(self, index):
        """Initialize the player.

        :param int index:
            Index of the player entity
        """
        super().__init__(index)
        self.id = self.uniqueid

    @property
    def hero(self):
        return self.heroes[self._active_hero_id]

    @hero.setter
    def hero(self, value):
        if not isinstance(value, Hero):
            raise ValueError(
                "Attempt to set player's hero to a non hero value {0}".format(value))
        if value.id not in self.heroes:
            raise ValueError(
                "Hero {0} not owned by player.".format(value))
        self._active_hero_id = value.id

    def calculate_total_level(self):
        """Calculate the total level of all of player's heroes."""
        return sum(hero.level for hero in self.heroes.values()) 
