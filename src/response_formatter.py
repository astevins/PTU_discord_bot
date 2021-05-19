def dict_to_str(dict):
    str = ""
    for key, val in dict.items():
        str = str + f"{key}: {val}\n"
    return str
