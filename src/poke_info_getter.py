from collections import OrderedDict
import pokepy

from response_formatter import dict_to_str


# class MoveList:

# class BaseStats:

# class Evolutions:

class InvalidRequest(Exception):
    """Invalid request - nonexistant pokemon, item, etc."""
    pass


class PokeInfoGetter:
    def __init__(self):
        self.client = pokepy.V2Client()

    def poke_overview(self, name):
        poke = self.__get_poke__(name)

        overview = OrderedDict()
        overview = {"Name": poke.name, "Id": poke.id}

        types = [entry.type.name for entry in poke.types]
        overview["Type"] = "/".join(types)

        abilities = [entry.ability.name for entry in poke.abilities]
        overview["Ability"] = "/".join(abilities)

        return dict_to_str(overview)

    def poke_pic(self, name, shiny=False, mega=False):
        poke = self.__get_poke__(name)
        if mega:
            poke = self.__get_poke__(f"{name}-mega")
        if shiny:
            return poke.sprites.front_shiny
        else:
            return poke.sprites.front_default

    def poke_stats(self, name):
        poke = self.__get_poke__(name)

        stats = OrderedDict();
        for entry in poke.stats:
            stats[entry.stat.name.title()] = entry.base_stat
        return dict_to_str(stats)

    def __get_poke__(self, name):
        try:
            pokes = self.client.get_pokemon(name)
            poke = pokes[0]
        except:
            raise InvalidRequest("Invalid pokemon name.")

        return poke

    def __get_poke_forms__(self, name):
        try:
            pokes = self.client.get_pokemon_form(f"{name}-mega")
            poke = pokes[0]
        except:
            raise InvalidRequest("Invalid pokemon name.")

        return poke
