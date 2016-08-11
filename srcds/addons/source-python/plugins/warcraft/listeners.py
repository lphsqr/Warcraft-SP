"""A module for the plugin's custom Source.Python listeners."""

# Source.Python imports
from listeners import ListenerManager
from listeners import ListenerManagerDecorator

__all__ = (
    'OnHeroLevelUp',
    'OnHeroLevelDown',
    'OnSkillUpgrade',
    'OnSkillDowngrade',
)


class OnHeroLevelUp(ListenerManagerDecorator):
    """Listener to notify when a hero gains a level.

    Arguments for callbacks:
        :class:`warcraft.entities.Hero` hero: Hero who leveled up
        :class:`warcraft.player.Player` player: Player whose hero it was
        :class:`int` levels: Amount of levels gained
    """
    manager = ListenerManager()


class OnHeroLevelDown(ListenerManagerDecorator):
    """Listener to notify when a hero loses a level.

    Arguments for callbacks:
        :class:`warcraft.entities.Hero` hero: Hero who leveled down
        :class:`warcraft.player.Player` player: Player whose hero it was
        :class:`int` levels: Amount of levels lost
    """
    manager = ListenerManager()


class OnSkillUpgrade(ListenerManagerDecorator):
    """Listener to notify when a skill is upgraded.

    Arguments for callbacks:
        :class:`warcraft.entities.Skill` skill: Skill which was upgraded
        :class:`warcraft.entities.Hero` hero: Hero whose skill it was
        :class:`warcraft.player.Player` player: Player whose hero it was
    """
    manager = ListenerManager()


class OnSkillDowngrade(ListenerManagerDecorator):
    """Listener to notify when a skill is downgraded.

    Arguments for callbacks:
        :class:`warcraft.entities.Skill` skill: Skill which was downgraded
        :class:`warcraft.entities.Hero` hero: Hero whose skill it was
        :class:`warcraft.player.Player` player: Player whose hero it was
    """
    manager = ListenerManager()
