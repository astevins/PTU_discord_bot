from src import dynamo_db_tools


def add_member_spread(guild_id, member_id, spreadsheet_name):
    print(f"Adding spreadsheet {spreadsheet_name} for member {member_id}")
    dynamo_db_tools.put_item_single_value(str(guild_id), str(member_id), spreadsheet_name)


def get_member_spread(guild_id, member_id):
    return dynamo_db_tools.get_item_single_value(str(guild_id), str(member_id))
