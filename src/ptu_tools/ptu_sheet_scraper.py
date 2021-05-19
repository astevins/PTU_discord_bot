from collections import OrderedDict
import gspread
import json
import os

from src import response_formatter

dir_path = os.path.dirname(os.path.realpath(__file__))

DICT_FILE = os.path.join(dir_path, "ptu_spread_cells.json")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_API_CREDENTIALS"))
TRAINER_SHEET = "Trainer"
COMBAT_SHEET = "Combat"

STATS = ["max hp", "curr hp", "atk", "def", "satk", "sdef", "spd"]
ALT_STATS = {"max_hp": "max hp", "current hp": "curr hp", "current_hp": "curr hp",
             "curr_hp": "curr hp", "attack": "atk", "defense": "def", "special attack": "satk",
             "special defense": "sdef", "speed": "spd"}
SKILLS = ["acrobatics", "athletics", "charm", "combat",
          "command", "general dd", "medicine ed", "occult ed",
          "poke ed", "tech ed", "focus", "guile", "intimidate",
          "intuition", "perception", "stealth", "survival"]
ALT_SKILLS = {"pokemon ed": "poke ed", "technology ed": "tech ed"}

STATS_FORMATTED = ["Max HP", "Curr HP", "ATK", "DEF", "SATK", "SDEF", "SPD"]
SKILLS_FORMATTED = ["Acrobatics", "Athletics", "Charm", "Combat",
                    "Command", "General Ed", "Medicine Ed", "Occult Ed",
                    "Poke Ed", "Tech Ed", "Focus", "Guile", "Intimidate",
                    "Intuition", "Perception", "Stealth", "Survival"]

instance = None


class InvalidInput(Exception):
    """Invalid input: stat name or skill name doesn't exist, etc."""
    pass


def get_instance():
    if instance:
        return instance
    else:
        return PtuSheetScraper()


def __check_skill_name__(skill_name):
    name = skill_name.lower()
    if name in SKILLS:
        return name
    if name in ALT_SKILLS:
        return ALT_SKILLS[name]
    raise InvalidInput(f"Invalid skill name. Choose one of {SKILLS_FORMATTED}")


def __check_stat_name__(stat_name):
    name = stat_name.lower()
    if name in STATS:
        return name
    if name in ALT_STATS:
        return ALT_STATS[name]
    raise InvalidInput(f"Invalid stat name. Choose one of {STATS_FORMATTED}")


class PtuSheetScraper:
    def __init__(self):
        self.gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)

        with open(DICT_FILE, 'r') as file:
            self.cells = json.loads(file.read())

    def get_trainer_name(self, file):
        return self.__get_cell_value__(file, TRAINER_SHEET, self.cells["trainer name"])

    def get_trainer_stat(self, file, stat_name):
        name = __check_stat_name__(stat_name)
        return self.__get_cell_value__(file, COMBAT_SHEET if name == "curr hp" else TRAINER_SHEET,
                                       self.cells[f"trainer {name}"])

    def get_poke_stat(self, file, poke_name, stat_name):
        name = __check_stat_name__(stat_name)
        return self.__get_cell_value__(file, poke_name, self.cells[f"poke {name}"])

    def get_all_trainer_stats(self, file):
        result = OrderedDict()
        max_hp = self.get_trainer_stat(file, "max hp")
        curr_hp = self.get_trainer_stat(file, "curr hp")
        result["HP"] = f"{curr_hp}/{max_hp}"
        for stat in STATS_FORMATTED:
            if stat.lower() == "curr hp" or stat.lower() == "max hp":
                continue
            else:
                result[stat] = self.get_trainer_stat(file, stat)
        return response_formatter.dict_to_str(result)

    def get_all_poke_stats(self, file, poke_name):
        result = OrderedDict()
        max_hp = self.get_poke_stat(file, poke_name, "max hp")
        curr_hp = self.get_poke_stat(file, poke_name, "curr hp")
        result["HP"] = f"{curr_hp}/{max_hp}"
        for stat in STATS_FORMATTED:
            if stat.lower() == "curr hp" or stat.lower() == "max hp":
                continue
            else:
                result[stat] = self.get_poke_stat(file, poke_name, stat)
        return response_formatter.dict_to_str(result)

    def get_trainer_skill_roll(self, file, skill_name):
        name = __check_skill_name__(skill_name)
        return self.__get_cell_value__(file, TRAINER_SHEET, self.cells[f"trainer {name}"])

    def get_poke_skill_roll(self, file, poke_name, skill_name):
        name = __check_skill_name__(skill_name)
        return self.__get_cell_value__(file, poke_name, self.cells[f"poke {name}"])

    def get_move_ac(self, file, sheet, move_name):
        cell = self.__get_move_cell__(file, sheet, move_name)
        return self.__get_cell_value_row_col__(file, sheet, cell.row, cell.col + 8)

    def get_move_dmg_roll(self, file, sheet, move_name):
        cell = self.__get_move_cell__(file, sheet, move_name)
        base = self.__get_cell_value_row_col__(file, sheet, cell.row, cell.col + 4)
        modifier = self.__get_cell_value_row_col__(file, sheet, cell.row, cell.col + 6)
        return base if modifier == "--" else f"{base}+{modifier}"

    def __get_move_cell__(self, file, sheet, move_name):
        move_name = move_name.lower().title()
        try:
            cell = self.__find_cell__(file, sheet, move_name)
        except Exception as err:
            if sheet == COMBAT_SHEET:
                raise InvalidInput(f"Trainer doesn't have the move {move_name}")
            raise InvalidInput(f"{sheet} doesn't have the move {move_name}")
        return cell

    def __get_cell_value__(self, file, sheet, cell):
        worksheet = self.__get_worksheet__(file, sheet)
        return worksheet.acell(cell).value

    def __get_cell_value_row_col__(self, file, sheet, row, col):
        worksheet = self.__get_worksheet__(file, sheet)
        return worksheet.cell(row, col).value

    def __find_cell__(self, file, sheet, content):
        worksheet = self.__get_worksheet__(file, sheet)
        return worksheet.find(content)

    def __get_worksheet__(self, file, sheet_name):
        try:
            sh = self.gc.open(file)
        except:
            raise InvalidInput(f"Failed to open google sheets file: {file}")

        try:
            worksheet = sh.worksheet(sheet_name)
        except:
            raise InvalidInput("Invalid worksheet name; did you enter a pokemon name incorrectly?")

        return worksheet
