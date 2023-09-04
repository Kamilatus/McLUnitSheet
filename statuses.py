import json
import mobs


def get_raw_status(file_name):
    file = open(file_name, 'rb')
    status_object = json.load(file)
    return status_object


def damage_over_time(status):
    if 'badger:damage_over_time' in status:
        damage_over_time = status['badger:damage_over_time']
        status['interval'] = damage_over_time['interval']
        status['damage'] = damage_over_time['damage']['damage_amount']
        if damage_over_time['damage']['damage_types']:
            status['damage types'] = damage_over_time['damage']['damage_types']
            if len(status['damage types']) == 1:
                status['damage types'] = status['damage types'][0]
        else:
            status['damage types'] = None
        del status['badger:damage_over_time']
    else:
        status['interval'] = None
        status['damage'] = None
        status['damage types'] = None


def granted_actions(status):
    if 'badger:granted_actions' in status:
        del status['badger:granted_actions']
        if status['name'] == 'bumped':
            status['additional notes'] = ['upward knockback']


def negated_statuses(status):
    if 'badger:negate_status' in status:
        status['negated statuses'] = status['badger:negate_status']['negated_status']
        del status['badger:negate_status']
    else:
        status['negated statuses'] = None


def movement_modifier(status):
    if 'badger:modifier_movement_speed' in status:
        status['speed mod'] = status['badger:modifier_movement_speed']['post_multiply']
        del status['badger:modifier_movement_speed']
    else:
        status['speed mod'] = None


def jump_modifier(status):
    if 'badger:modifier_jump_height' in status:
        status['jump mod'] = status['badger:modifier_jump_height']['post_multiply']
        del status['badger:modifier_jump_height']
    else:
        status['jump mod'] = None


def disables_movement_and_actions(status):
    status['disables movement and actions'] = [False, False]
    if 'badger:disables_movement' in status:
        status['disables movement and actions'][0] = True
        del status['badger:disables_movement']
    if 'badger:disables_actions' in status:
        status['disables movement and actions'][1] = True
        del status['badger:disables_actions']
    if status['disables movement and actions'] == [False, False]:
        status['disables movement and actions'] = None


def other_shit(status):
    if 'badger:modifier_knockback_resistance' in status:
        status['knockback resistance modifier'] = status['badger:modifier_knockback_resistance']['post_multiply']
        del status['badger:modifier_knockback_resistance']
    if 'badger:modifier_knockback_force' in status:
        status['knockback force modifier'] = status['badger:modifier_knockback_force']['post_multiply']
        del status['badger:modifier_knockback_force']
    if 'badger:modifier_resistance' in status:
        status['resistance modifiers'] = status['badger:modifier_resistance']['resistances']
        del status['badger:modifier_resistance']
    if 'badger:modifier_size' in status:
        status['size modifier'] = status['badger:modifier_size']['scale']
        del status['badger:modifier_size']
    stuff_to_change = []
    for stuff in status:
        if 'badger:' in stuff:
            stuff_to_change.append(stuff)
    for stuff in stuff_to_change:
        status[stuff.removeprefix('badger:')] = status[stuff]
        del status[stuff]
    for number_stuff in ['time', 'resistance time', 'damage', 'interval', 'speed mod', 'jump mod']:
        if status[number_stuff] is not None:
            status[number_stuff] = float(status[number_stuff])


def fix_status(status):
    status = status['minecraft:entity']['components']
    status['name'] = status['badger:status']['applied_name']
    default_resistance = status['badger:status']['default_resistance']
    status['time'] = default_resistance['time']
    status['resistance time'] = default_resistance['resistance_persist_time']
    if status['resistance time'] <= 0:
        status['resistance time'] = None
    del status['badger:status']
    if 'badger:counterattacker' in status:
        del status['badger:counterattacker']
    granted_actions(status)
    damage_over_time(status)
    negated_statuses(status)
    movement_modifier(status)
    jump_modifier(status)
    disables_movement_and_actions(status)
    other_shit(status)
    mobs.additional_notes(status, False)
    return status


def get_statuses(file_names):
    statuses = []
    for file_name in file_names:
        statuses.append(fix_status(get_raw_status(file_name)))
    return statuses
