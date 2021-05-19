from collections import OrderedDict
import dice

from src.ptu_tools import ptu_sheet_scraper
from src import response_formatter


def roll_trainer_skill(file, skill_name):
    sheet_scraper = ptu_sheet_scraper.get_instance()
    to_roll = sheet_scraper.get_trainer_skill_roll(file, skill_name)
    return response_formatter.dict_to_str(__roll__(to_roll))


def roll_poke_skill(file, poke_name, skill_name):
    sheet_scraper = ptu_sheet_scraper.get_instance()
    to_roll = sheet_scraper.get_poke_skill_roll(file, poke_name, skill_name)
    return response_formatter.dict_to_str(__roll__(to_roll))


def roll_poke_attack(file, poke_name, move_name):
    return __roll_attack__(file, poke_name, move_name)


def roll_trainer_attack(file, move_name):
    return __roll_attack__(file, ptu_sheet_scraper.TRAINER_SHEET, move_name)


def __roll_attack__(file, sheet, move_name):
    result = OrderedDict()
    sheet_scraper = ptu_sheet_scraper.get_instance()
    ac = sheet_scraper.get_move_ac(file, sheet, move_name)
    acc_roll = __roll_total_only__("d20")
    result["Move AC"] = ac
    result["Accuracy Roll"] = acc_roll
    to_roll = sheet_scraper.get_move_dmg_roll(file, sheet, move_name)
    dmg_roll = __roll__(to_roll)
    result["Damage Dice"] = dmg_roll["Rolled"]
    result["Damage Roll"] = f"{dmg_roll['Result']} = {dmg_roll['Total']}"
    return response_formatter.dict_to_str(result)


def __roll__(to_roll):
    modifier = 0
    if '+' in to_roll:
        roll_split = to_roll.split("+")
        to_roll = roll_split[0]
        modifier = sum(map(int, roll_split[1:]))

    roll = dice.roll(to_roll)
    result = OrderedDict()
    result["Rolled"] = f"{to_roll} + {modifier}"
    modifier_str = f"+ {modifier}" if modifier else ""
    result["Result"] = f"{roll} {modifier_str}"
    try:
        result["Total"] = sum(roll) + modifier
    except:
        result["Total"] = roll
    return result


def __roll_total_only__(to_roll):
    return dice.roll(f"{to_roll}t")
