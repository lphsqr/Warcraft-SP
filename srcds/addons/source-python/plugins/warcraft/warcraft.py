"""Main entry point for the plugin."""

# Source.Python imports
from commands import CommandReturn
from commands.client import ClientCommand
from commands.say import SayCommand
from events import Event
from menus import ListMenu
from menus import ListOption
from menus import PagedMenu
from menus import PagedOption
from messages import SayText2
from players.dictionary import PlayerDictionary
from translations.strings import LangStrings

# Warcraft imports
import warcraft.database
import warcraft.heroes
import warcraft.player


# ======================================================================
# >> FUNCTIONS
# ======================================================================

def _new_player(index):
    """Create a player and load his data from the database."""
    player = warcraft.player.Player(index)

    # Give the player all heroes available by his total level
    total_level = player.calculate_total_level()
    for hero_id, hero_class in heroes.items():
        if hero_id in player.heroes:
            continue
        if hero_class.required_level <= total_level:
            player.heroes[hero_id] = heroes[hero_id](player)

    # Set player's active hero
    player.hero = next(iter(player.heroes.values()))

    return player


# ======================================================================
# >> SKILL EXECUTION CALLBACKS
# ======================================================================

@Event('player_jump', 'player_spawn', 'player_disconnect')
def _execute_individual_skills(event):
    """Execute skills for events with only one player."""
    event_args = event.variables.as_dict()
    player = players.from_userid(event_args.pop('userid'))
    if player.team in (2, 3):
        event_args['player'] = player
        player.hero.execute_skills(event.name, event_args)


# Converter from event's name to attacker's and victim's event names
_event_name_conversions = {
    'player_death': ('player_kill', 'player_death'),
    'player_hurt': ('player_attack', 'player_victim'),
}


@Event('player_death', 'player_hurt')
def _execute_interaction_skills(event):
    """Execute skills for events with two players."""
    if not event['attacker'] or event['attacker'] == event['userid']:
        return
    event_args = event.variables.as_dict()

    attacker = players.from_userid(event_args.pop('attacker'))
    victim = players.from_userid(event_args.pop('userid'))
    event_args.update(attacker=attacker, victim=victim)

    event_names = _event_name_conversions[event.name]
    event_args['player'] = attacker
    attacker.hero.execute_skills(event_names[0], event_args)
    event_args['player'] = victim
    victim.hero.execute_skills(event_names[1], event_args)


# ======================================================================
# >> EXPERIENCE POINT CALLBACKS
# ======================================================================

@Event('player_death')
def _give_xp_from_kill(event):
    """Give the killing player XP from his kill."""
    if not event['attacker'] or event['attacker'] == event['userid']:
        return
    attacker = players.from_userid(event['attacker'])
    attacker.hero.xp += 45 if event['headshot'] else 30


# ======================================================================
# >> MISCELLANEOUS CALLBACKS
# ======================================================================

@Event('player_spawn')
def _send_hero_info_message(event):
    """Send the player his current hero's information."""
    player = players.from_userid(event['userid'])
    if player.steamid != 'BOT':
        _hero_info_message.send(player.index, hero=player.hero)


@warcraft.listeners.OnHeroLevelUp
def _send_level_up_message(hero, player, levels):
    """Send a level up message to the player whose hero leveled up."""
    _level_up_message.send(player.index, hero=hero)


# ======================================================================
# >> CLIENT/SAY COMMANDS
# ======================================================================

@ClientCommand('warcraft')
@SayCommand('warcraft')
def _warcraft_command_callback(command, player_index, only=None):
    main_menu.send(player_index)
    return CommandReturn.BLOCK

@ClientCommand('changehero')
@SayCommand('changehero')
def _changehero_command_callback(command, player_index, only=None):
    change_hero_menu.send(player_index)
    return CommandReturn.BLOCK

@ClientCommand('spendskills')
@SayCommand('spendskills')
def _spendskills_command_callback(command, player_index, only=None):
    spend_skills_menu.send(player_index)
    return CommandReturn.BLOCK

@ClientCommand('resetskills')
@SayCommand('resetskills')
def _resetskills_command_callback(command, player_index, only=None):
    players[player_index].hero.reset_skills()
    return CommandReturn.BLOCK

@ClientCommand('heroinfo')
@SayCommand('heroinfo')
def _heroinfo_command_callback(command, player_index, only=None):
    _hero_info_message.send(player_index, hero=players[player_index].hero)
    return CommandReturn.BLOCK


# ======================================================================
# >> GLOBALS
# ======================================================================

# A dictionary of all the players, uses indexes as keys
players = PlayerDictionary(_new_player)

# A dictionary of the heroes from heroes.__init__.get_heroes
heroes = {hero.class_id: hero for hero in warcraft.heroes.get_heroes()}

# Translations for the Warcraft plugin
_tr = LangStrings('warcraft')
_hero_info_message = SayText2(_tr['Hero Info'])
_level_up_message = SayText2(_tr['Level Up'])


# ======================================================================
# >> MENUS
# ======================================================================

def _on_main_menu_build(menu, player_index):
    """Build the main menu."""
    player = players[player_index]
    menu.clear()
    menu.description = player.hero.name
    menu.extend([
        PagedOption(_tr['Change Hero'], change_hero_menu),
        PagedOption(_tr['Spend Skills'], spend_skills_menu),
        PagedOption(_tr['Reset Skills'], 'reset'),
        PagedOption(_tr['Hero Infos'], hero_infos_menu),
    ])

def _on_main_menu_select(menu, player_index, choice):
    """React to a main menu selection."""
    player = players[player_index]
    if choice.value == 'reset':
        player.hero.reset_skills()
        return menu
    return choice.value

main_menu = PagedMenu(
    title=_tr['Main Menu'],
    build_callback=_on_main_menu_build,
    select_callback=_on_main_menu_select,
)


def _on_change_hero_menu_build(menu, player_index):
    """Build the change hero menu."""
    player = players[player_index]
    menu.clear()
    menu.description = player.hero.name
    total_level = player.calculate_total_level()
    for hero_id, hero_class in heroes.items():
        if hero_id in player.heroes or hero_class.required_level <= total_level:
            text = _tr['Owned Hero Text'].get_string(hero=player.heroes[hero_id])
            menu.append(PagedOption(text, hero_class, True, True))
        else:
            text = _tr['Unowned Hero Text'].get_string(hero=hero_class)
            menu.append(PagedOption(text, None, False, False))

def _on_change_hero_menu_select(menu, player_index, choice):
    """React to a change hero menu selection."""
    player = players[player_index]
    hero_id = choice.value.class_id
    if hero_id == player.hero.class_id:
        return
    if hero_id not in player.heroes:
        player.heroes[hero_id] = choice.value(player)
    player.hero = player.heroes[hero_id]
    player.client_command('kill', True)

change_hero_menu = PagedMenu(
    title=_tr['Change Hero'],
    build_callback=_on_change_hero_menu_build,
    select_callback=_on_change_hero_menu_select,
    parent_menu=main_menu,
)


def _on_spend_skills_menu_build(menu, player_index):
    """Build the spend skills menu."""
    player = players[player_index]
    hero = player.hero
    menu.clear()
    menu.title = hero.name
    menu.description = _tr['Skill Points'].get_string(skill_points=hero.skill_points)
    for skill in hero.skills.values():
        if skill.required_level <= hero.level:
            text = _tr['Owned Skill Text'].get_string(skill=skill)
        else:
            text = _tr['Unowned Skill Text'].get_string(skill=skill)
        can_upgrade = hero.can_upgrade_skill(skill)
        menu.append(PagedOption(text, skill, can_upgrade, can_upgrade))

def _on_spend_skills_menu_select(menu, player_index, choice):
    """React to an spend skills menu selection."""
    hero = players[player_index].hero
    if hero.can_upgrade_skill(choice.value):
        hero.upgrade_skill(choice.value)
    return menu

spend_skills_menu = PagedMenu(
    parent_menu=main_menu,
    build_callback=_on_spend_skills_menu_build,
    select_callback=_on_spend_skills_menu_select,
)


def _on_hero_infos_menu_build(menu, player_index):
    """Build the hero infos menu."""
    menu.clear()
    for hero_class in heroes.values():
        menu.append(PagedOption(hero_class.name, hero_class))

def _on_hero_infos_menu_select(menu, player_index, choice):
    """React to a hero infos menu selection."""
    return HeroInfoMenu(choice.value, parent_menu=hero_infos_menu)

hero_infos_menu = PagedMenu(
    title=_tr['Hero Infos'],
    parent_menu=main_menu,
    build_callback=_on_hero_infos_menu_build,
    select_callback=_on_hero_infos_menu_select,
)


class HeroInfoMenu(ListMenu):
    """A menu class for displaying individual hero's information."""

    def __init__(self, hero_class, *args, **kwargs):
        """Initialize the hero info menu with a hero."""
        super().__init__(*args, **kwargs)
        self.hero_class = hero_class
        self.items_per_page = 3
        self.build_callback = self._build_callback

    @staticmethod
    def _build_callback(menu, player_index):
        """Build the menu."""
        menu.clear()
        menu.title = menu.hero_class.name
        for skill_cls in menu.hero_class.skill_classes:
            text = '{s.name}\n{s.description}'.format(s=skill_cls)
            menu.append(ListOption(text))
