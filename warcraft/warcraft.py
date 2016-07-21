"""Main entry point for the plugin."""

# Source.Python imports
from events import Event

# Warcraft imports
import warcraft.player


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
# >> GLOBALS
# ======================================================================

# A dictionary of all the players, uses indexes as keys
players = PlayerDictionary(warcraft.player.Player)
