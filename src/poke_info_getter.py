import json
from collections import OrderedDict
import pokepy
import requests

from response_formatter import dict_to_str

PIC_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"


class InvalidRequest(Exception):
    """Invalid request - nonexistant pokemon, item, etc."""
    pass


class PokeInfoGetter:
    def __init__(self):
        self.client = pokepy.V2Client()

    def poke_types(self, name, mega):
        poke = self.__get_poke__(name, mega)

        overview = OrderedDict()
        overview["Name"] = poke.name
        types = [entry.type.name for entry in poke.types]
        overview["Type"] = "/".join(types)

        return dict_to_str(overview)

    def poke_sprite(self, name, shiny=False, mega=False):
        poke = self.__get_poke__(name, mega)
        if shiny:
            return poke.sprites.front_shiny
        else:
            return poke.sprites.front_default

    def poke_pic(self, name, mega=False):
        poke = self.__get_poke__(name, mega)

        poke_id = poke.id
        return f"{PIC_URL}{poke_id}.png"

    def poke_stats(self, name):
        poke = self.__get_poke__(name)

        stats = OrderedDict()
        for entry in poke.stats:
            stats[entry.stat.name.title()] = entry.base_stat
        return dict_to_str(stats)

    def __get_poke__(self, name, mega):
        try:
            if mega:
                name = f"{name}-mega"
            pokes = self.client.get_pokemon(name)
            poke = pokes[0]
        except:
            raise InvalidRequest("Invalid pokemon name.")

        return poke
