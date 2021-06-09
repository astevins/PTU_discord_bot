import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import dynamo_db_tools
import poke_info_getter
from src.ptu_tools import ptu_sheet_scraper, ptu_member_info_tool, ptu_roller

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PFX = "*"


def setIntents():
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.messages = True
    intents.reactions = True
    return intents


bot = commands.Bot(intents=setIntents(), command_prefix=PFX)
pi = poke_info_getter.PokeInfoGetter()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    for guild in bot.guilds:
        dynamo_db_tools.create_table_if_new(str(guild.id))


@bot.event
async def on_member_join(member):
    print(f"{member.name} has joined the server!")
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to the world of Pokemon!")


@bot.command(name="pic", help="*pic [pokemon name]: gets official artwork")
async def pic(context, *args):
    mega = False
    name = ""
    if "mega" in args:
        mega = True
    for arg in args:
        if not arg.lower() == "mega":
            name = arg.lower()
            break

    try:
        response = pi.poke_pic(name, mega)
    except Exception as e:
        print(e)
        response = "Invalid pokemon name"
    await context.send(response)


class CommandArgs:
    def __init__(self, shiny=False, mega=False, name=""):
        self.shiny = shiny
        self.mega = mega
        self.name = name


def __parse_args__(args) -> CommandArgs:
    shiny = False
    mega = False
    name = ""
    if "shiny" in args:
        shiny = True
    if "mega" in args:
        mega = True
    for arg in args:
        if not arg.lower() == "shiny" and not arg.lower() == "mega":
            name = arg.lower()
            break

    return CommandArgs(shiny=shiny, mega=mega, name=name)


@bot.command(name="sprite", help="*sprite [pokemon name]: gets sprite")
async def sprite(context, *args):
    parsed_args: CommandArgs = __parse_args__(args)

    try:
        response = pi.poke_sprite(parsed_args.name, parsed_args.shiny, parsed_args.mega)
    except:
        response = "Invalid pokemon name"
    await context.send(response)


@bot.command(name="type", help="*type [pokemon name]: gives pokemon type(s)")
async def type_(context, *args):
    parsed_args: CommandArgs = __parse_args__(args)

    try:
        response = pi.poke_types(parsed_args.name, parsed_args.mega)
    except poke_info_getter.InvalidRequest as err:
        response = f"Error:{err}"

    await context.send(response)


@bot.command(name="dex", help="*dex [pokemon name]: gives pokemon dex entry")
async def dex(context, *args):
    name = None
    version = None
    for arg in args:
        if not name:
            name = arg.lower()
        else:
            version = arg.lower()
            break

    try:
        response = pi.poke_dex(name, version)
    except poke_info_getter.InvalidRequest as err:
        response = f"Error:{err}"

    await context.send(response)


@bot.command(name="info", help="*info [pokemon name]: gives pokemon picture, type, and flavor text")
async def info(context, *args):
    await sprite(context, *args)
    await type_(context, *args)
    await dex(context, *args)


@bot.command(name="skill", help="*skill [skill] for trainer OR *skill [pokemon name] [skill]")
async def roll(context, *args):
    guild_id = context.guild.id
    sender = context.message.author

    if len(context.message.mentions) == 1:
        relevant_member = context.message.mentions[0]
        print(relevant_member.id)
    else:
        relevant_member = sender

    try:
        spread_name = ptu_member_info_tool.get_member_spread(guild_id, relevant_member.id)
        if len(args) == 1 + len(context.message.mentions):
            skill_name = args[0]
            result = ptu_roller.roll_trainer_skill(spread_name, skill_name)
            response = f"Rolling {skill_name} for {spread_name}:\n{result}"
        elif len(args) == 2 + len(context.message.mentions):
            poke_name = args[0]
            skill_name = args[1]
            result = ptu_roller.roll_poke_skill(spread_name, poke_name, skill_name)
            response = f"Rolling {skill_name} for {poke_name}:\n{result}"
        else:
            response = f"Invalid number of arguments: {len(args)}"
    except Exception as err:
        response = f"Error: {err}"

    await context.send(response)


@bot.command(name="stat", help="*stat [stat] for trainer OR *stat [pokemon name] [stat]")
async def stat(context, *args):
    guild_id = context.guild.id
    sender = context.message.author

    if len(context.message.mentions) == 1:
        relevant_member = context.message.mentions[0]
        print(relevant_member.id)
    else:
        relevant_member = sender

    try:
        spread_name = ptu_member_info_tool.get_member_spread(guild_id, relevant_member.id)
        if len(args) == 1 + len(context.message.mentions):
            stat_name = args[0]
            result = ptu_sheet_scraper.get_instance().get_trainer_stat(spread_name, stat_name)
            response = f"{stat_name} for {spread_name}: {result}"
        elif len(args) == 2 + len(context.message.mentions):
            poke_name = args[0]
            stat_name = args[1]
            result = ptu_sheet_scraper.get_instance().get_poke_stat(spread_name, poke_name, stat_name)
            response = f"{stat_name} for {poke_name}: {result}"
        else:
            response = f"Invalid number of arguments: {len(args)}"
    except Exception as err:
        response = f"Error: {err}"

    await context.send(response)


@bot.command(name="stats", help="*stats for trainer OR *stats [pokemon name]")
async def stats(context, *args):
    guild_id = context.guild.id
    sender = context.message.author
    if len(context.message.mentions) == 1:
        relevant_member = context.message.mentions[0]
        print(relevant_member.id)
    else:
        relevant_member = sender

    try:
        spread_name = ptu_member_info_tool.get_member_spread(guild_id, relevant_member.id)
        print(spread_name)
        if len(args) == 0 + len(context.message.mentions):
            result = ptu_sheet_scraper.get_instance().get_all_trainer_stats(spread_name)
            trainer_name = ptu_sheet_scraper.get_instance().get_trainer_name(spread_name)
            response = f"Stats for {trainer_name}:\n{result}"
        elif len(args) == 1 + len(context.message.mentions):
            poke_name = args[0]
            result = ptu_sheet_scraper.get_instance().get_all_poke_stats(spread_name, poke_name)
            response = f"Stats for {poke_name}:\n{result}"
        else:
            response = f"Invalid number of arguments: {len(args)}"
    except Exception as err:
        response = f"Error: {err}"

    await context.send(response)


@bot.command(name="move", help="*move [move name] for trainer OR *move [pokemon name] [move name]")
async def move(context, *args):
    guild_id = context.guild.id
    sender = context.message.author

    if len(context.message.mentions) == 1:
        relevant_member = context.message.mentions[0]
        print(relevant_member.id)
    else:
        relevant_member = sender

    try:
        spread_name = ptu_member_info_tool.get_member_spread(guild_id, relevant_member.id)
        if len(args) == 1 + len(context.message.mentions):
            move_name = args[0]
            response = ptu_roller.roll_trainer_attack(spread_name, move_name)
        elif len(args) == 2 + len(context.message.mentions):
            poke_name = args[0]
            move_name = args[1]
            response = ptu_roller.roll_poke_attack(spread_name, poke_name, move_name)
        else:
            response = f"Invalid number of arguments: {len(args)}"
    except Exception as err:
        response = f"Error: {err}"

    await context.send(response)


@bot.command(name="spreadsheet", help="*spreadsheet [spreadsheet name]: links spreadsheet to user")
async def spreadsheet(context, spread_name):
    guild_id = context.guild.id
    sender = context.message.author
    try:
        ptu_member_info_tool.add_member_spread(guild_id, sender.id, spread_name)
        response = (f"Successfully updated spreadsheet for {sender.name}\n"
                    f"Make sure to share your google sheet with:\n"
                    f"ptu-spreadsheet-bot@arceusbot-312120.iam.gserviceaccount.com")
    except Exception as err:
        response = f"Error: {err}"

    await context.send(response)


bot.run(TOKEN)
