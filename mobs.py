import json


def get_entity(file_name):
    fixed_json = ''
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if '/' not in line:
                fixed_json += line
            else:
                if '{' in line:
                    fixed_json += '\n{\n'
                if '}' in line:
                    fixed_json += '\n}\n'
                if ',' in line:
                    fixed_json += ','

    mob = json.loads(fixed_json)
    return mob['minecraft:entity']


def attack_data_cleanup(attack):
    blacklist = ['on_hit_target_trigger', 'activation_trigger', 'trigger', 'predictive_windup', 'suicide_action']
    for word in blacklist:
        if word in attack:
            del attack[word]
    if 'interruptible' in attack:
        if len(attack['interruptible']) == 0:
            del attack['interruptible']
    if 'starts_disabled' in attack:
        if not attack['starts_disabled']:
            del attack['starts_disabled']


def attack_cooldown(attack):
    state_machine = attack['state_machine']
    cooldown = 0.0
    for time in state_machine:
        cooldown += state_machine[time]
    attack.update({'state_machine': cooldown})
    attack['cooldown'] = attack['state_machine']
    del attack['state_machine']


def is_ranged_attack(name):
    is_burst_shot = name == 'burst_shot_1' or ('close_shot' in name and name != 'close_shot_knockback')
    other_attack_names = ['mud_attack', 'ranged_attack', 'arc', 'spit_attack']
    is_other_attack = any(attack_name in name for attack_name in other_attack_names)
    return is_burst_shot or is_other_attack


def attack_damage(attack, game_path):
    if attack['name'] == 'ranged_attack':
        unusual_ranged_attack(attack, 'proj_boulder_fallenwarrior_impact_aoe.json', game_path)
    elif attack['name'] == 'magma_boss_direct_shot':
        unusual_ranged_attack(attack, 'proj_magma_block_impact_aoe.json', game_path)
    elif attack['name'] == 'engineer_grenade':
        unusual_ranged_attack(attack, 'proj_engineer_grenade_impact_aoe.json', game_path)
    elif attack['name'] == 'piggo_lava_launcher_volley':
        unusual_ranged_attack(attack, 'proj_magma_block_impact_aoe.json', game_path)
    elif attack['name'] == 'magma_boss_lava_geyser':
        unbreakable_geyser(attack, game_path)
    elif is_ranged_attack(attack['name']):
        attack['damage'] = attack['shoot']['damage']['damage_amount']
        attack['damage_types'] = attack['shoot']['damage']['damage_types']
        del attack['shoot']
    else:
        attack['damage'] = attack['shape_area_damage']['damage']['damage_amount']
        attack['damage_types'] = attack['shape_area_damage']['damage']['damage_types']
        del attack['shape_area_damage']


def attack_range(attack):
    if 'accuracy' in attack:
        attack['min range'] = attack['accuracy']['min_range']
        attack['max range'] = attack['accuracy']['max_range']
        del attack['accuracy']
    if 'range' in attack:
        attack['max range'] = attack['range']['max_range']
        if 'min_range' in attack['range']:
            attack['min range'] = attack['range']['min_range']
        del attack['range']
    if 'min range' not in attack:
        attack['min range'] = 0
    if 'max range' not in attack:
        attack['max range'] = '?'
    if 'shoot' in attack:
        del attack['shoot']


def fix_attack(attack, game_path):
    zero_damage = ['axe_special_fast', 'spawn', 'mud_attack', 'geyser_attack_', 'tired_recovery',
                   'seeker_special_fast', 'cube_rain', 'aoe_', 'spawn', 'grenade_attack']
    attack_data_cleanup(attack)
    if attack['name'] == 'support_enemy_retreat':
        attack['damage'] = 0
        attack['cooldown'] = '?'
        attack_range(attack)
        return attack
    if any(name in attack['name'] for name in zero_damage):
        attack['damage'] = 0
    else:
        attack_damage(attack, game_path)
    if 'aoe_' not in attack['name']:
        attack_cooldown(attack)
    else:
        attack['cooldown'] = '?'
    attack_range(attack)

    return attack


def attacks(mob, game_path):
    mob_attacks = mob['components']['badger:target_actions']['actions']
    attacks_list = []
    if name(mob) == 'grenadier':
        grenadier_attacks(attacks_list, game_path)
    for attack in mob_attacks:
        if 'approach' not in attack['name'] and 'combat_position' not in attack['name']:
            fixed_attack = fix_attack(attack, game_path)
            additional_notes(fixed_attack, True)
            attacks_list.append(fixed_attack)
    return attacks_list


def unusual_ranged_attack(attack, impact_file, game_path):
    path = game_path + 'entities\\' + impact_file
    projectile_object = get_entity(path)
    projectile_damage_data = projectile_object['components']['badger:aoe']['damage_effects'][0]
    attack['damage'] = projectile_damage_data['damage']
    attack['damage_types'] = projectile_damage_data['damage_types']
    attack_range(attack)


def unbreakable_geyser(attack, game_path):
    path_spawner = game_path + 'entities\\spawner_piglin_magma_boss_lava_geyser.json'
    path_impact = game_path + 'entities\\impact_lava_geyser.json'
    spawner_object = get_entity(path_spawner)
    impact_object = get_entity(path_impact)
    spawner_data = spawner_object['components']['badger:buildable_spawner']
    impact_data = impact_object['components']['badger:target_actions']['actions'][0]
    attack['damage'] = impact_data['shape_area_damage']['damage']['damage_amount']
    attack['damage_types'] = []
    attack['activation time'] = impact_data['state_machine']['activation_time']
    attack['spawn rate'] = spawner_data['rate']
    attack['spawn cap'] = spawner_data['cap']
    attack['min radius'] = spawner_data['min_radius']
    attack['max radius'] = spawner_data['max_radius']
    attack['batch'] = spawner_data['batch']
    attack['geyser spawner removal time'] = spawner_object['components']['badger:removal_time']['time']


def grenadier_attacks(attacks_list, game_path):
    projectile = get_entity(game_path + 'entities\\proj_grenade_impact.json')
    projectile_attacks = projectile['components']['badger:aoe']['damage_effects']
    for attack in projectile_attacks:
        damage = attack['damage']
        fix_attack(attack, game_path)
        attack['damage'] = damage
        additional_notes(attack, True)
        attacks_list.append(attack)


def health(mob):
    return mob['components']['badger:health']['max_health']


def speed(mob):
    return mob['components']['badger:movement']['move_speed']


def wander(mob):
    if 'badger:wander' in mob['components']:
        return mob['components']['badger:wander']
    else:
        return {'wander_frequency': '?',
                'wander_radius': '?'}


# general, mob, buildable, wall
def targeting_range(mob, targeting_type):
    targeting_priorities = mob['components']['badger:targeting']['targeting_priorities']
    for target in targeting_priorities:
        if targeting_type in target['name']:
            return target['max_range']
    if targeting_type == 'general':
        for target in targeting_priorities:
            if target['name'] == 'cavalry_enemy_charge' or 'ally' in target['name']:
                return target['max_range']
    return '?'


def resists(mob):
    return mob['components']['badger:damage_receiver']['damage_resistances']


def name(mob):
    name = mob['description']['identifier']
    if 'mob' in name:
        return name.removeprefix('badger:mob_')
    else:
        return name.removeprefix('badger:piglin_')


def first_of_stone_targeting(mob):
    targeting_priorities = mob['components']['badger:targeting']['targeting_priorities']
    for target in targeting_priorities:
        if target['name'] == 'ally_giant_enemy_ranged':
            mob['targeting_range - general'] = target['max_range']
            mob['targeting_range - mobs'] = target['max_range']
        if target['name'] == 'ally_giant_buildable_ranged':
            mob['targeting_range - buildables'] = target['max_range']
        if target['name'] == 'ally_giant_wall_ranged':
            mob['targeting_range - walls'] = target['max_range']


def defense(mob):
    mob['name'] = name(mob)
    del mob['description'], mob['mushroom_data']
    mob['health'] = health(mob)
    mob['speed'] = speed(mob)
    mob['frequency'] = wander(mob)['wander_frequency']
    mob['radius'] = wander(mob)['wander_radius']
    mob['general'] = targeting_range(mob, 'general')
    mob['mobs'] = targeting_range(mob, 'mob')
    mob['buildables'] = targeting_range(mob, 'buildable')
    mob['walls'] = targeting_range(mob, 'wall')
    mob['resistances'] = resists(mob)
    del mob['components']


def additional_notes(attack, is_mob):
    if is_mob:
        regular_values = ['name', 'damage', 'cooldown', 'min range', 'max range', 'damage_types', 'additional notes']
    else:
        regular_values = ['name', 'time', 'resistance time', 'interval', 'damage', 'damage types',
                          'negated statuses', 'speed mod', 'jump mod',
                          'disables movement and actions','additional notes']
    to_delete = []
    attack['additional notes'] = []
    for value in attack:
        if value not in regular_values:
            attack['additional notes'].append(value + ': ' + str(attack[value]))
            to_delete.append(value)
    for value in to_delete:
        if value in attack:
            del attack[value]
