from collections import OrderedDict
import pokepy
import requests

from response_formatter import dict_to_str

PIC_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"


class InvalidRequest(Exception):
    """Invalid request - nonexistant pokemon, item, etc."""
    pass


def __is_requested_dex_entry__(flavor_text, version):
    return ((flavor_text.version.name == version or not version)
            and flavor_text.language.name == 'en')


class PokeInfoGetter:
    def __init__(self):
        self.client = pokepy.V2Client()

    def poke_types(self, name, mega):
        poke = self.__get_poke__(name, mega)

        response = OrderedDict()
        types = [entry.type.name for entry in poke.types]
        response["Type"] = "/".join(types)

        return dict_to_str(response)

    def poke_dex(self, name, version=None):
        poke = self.__get_poke__(name, mega=False, species=True)

        response = OrderedDict()

        for flavor_text in poke.flavor_text_entries:
            if __is_requested_dex_entry__(flavor_text, version):
                text = flavor_text.flavor_text.replace('\n', ' ')
                response[flavor_text.version.name] = text
                return dict_to_str(response)

        raise InvalidRequest(f"No dex entry found for version: {version}")

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

    def __get_poke__(self, name, mega, species=False):
        try:
            if mega:
                name = f"{name}-mega"
            if species:
                poke = self.client.get_pokemon_species(name)
            else:
                poke = self.client.get_pokemon(name)
        except Exception as e:
            print(e)
            raise InvalidRequest(f"Invalid pokemon name: {name}")

        return poke
