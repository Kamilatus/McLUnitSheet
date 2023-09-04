import os
import time
import mobs
import sheets
import statuses

game_to_badger_path = '\\data\\behavior_packs\\badger\\'


def validate_path(badger_path):
    if find('mob', badger_path + 'entities'):
        print('Game found. If it doesn\'t crash, you\'ll see \"Done\" in a moment.')
        return badger_path
    else:
        return validate_path(politely_ask_for_new_path(badger_path))


def politely_ask_for_new_path(badger_path):
    game_path = badger_path.removesuffix(game_to_badger_path)
    print(f"Game not found at location: \"{game_path}\"")
    new_path = input("Type the a path or you'll die: ")
    return new_path + game_to_badger_path


def find(pattern, badger_path):
    found_files = []
    for root, dirs, files in os.walk(badger_path):
        for name in files:
            if name.startswith(pattern):
                found_files.append(os.path.join(root, name))
    return found_files


def fix_list(files_list):
    fixed_list = []
    blacklist = ['ai.', 'campaign.', 'nis.', 'instant', 'onboarding', 'arena', 'thrower']
    for file in files_list:
        if not any(word in file for word in blacklist):
            fixed_list.append(file)
    return fixed_list


time.sleep(2)
game_path = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\MinecraftLegends'
badger_path = game_path + game_to_badger_path
badger_path = validate_path(badger_path)
time.sleep(2)
files_friendly = fix_list(find('mob_', badger_path + 'entities'))
files_piglins = fix_list(find('piglin_', badger_path + 'entities'))
files_statuses = find('status', badger_path + 'status_effects')

friendly = []
for file in files_friendly:
    friendly.append(mobs.get_entity(file))
piglins = []
for file in files_piglins:
    piglins.append(mobs.get_entity(file))
workbook = sheets.create_sheets()
sheets.fill_sheet_attacks(friendly, workbook['Friendly mobs - Attacks'], badger_path)
sheets.fill_sheet_attacks(piglins, workbook['Piglins - Attacks'], badger_path)
sheets.fill_sheet_defense(friendly, workbook['Friendly mobs - Defense'])
sheets.fill_sheet_defense(piglins, workbook['Piglins - Defense'])

statuses = statuses.get_statuses(files_statuses)
sheets.fill_sheet_statuses(statuses, workbook['Statuses'])

sheets.format_sheets(workbook)
workbook.save('McL.xlsx')

print('Done')
