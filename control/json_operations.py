import json
import os

FILE_NAME = 'settings.json'


def set_dimension(x: int = 500, y: int = 500, width: int = 500, height: int = 500):
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            json_obiekt = json.load(f)
            dim = json_obiekt['dimensions']
            json_obiekt['dimensions']['x'] = x
            json_obiekt['dimensions']['y'] = y
            json_obiekt['dimensions']['width'] = width - x
            json_obiekt['dimensions']['height'] = height - y
        with open(FILE_NAME, 'w') as f:
            json.dump(json_obiekt, f, indent=4)
    else:
        with open('settings.json', 'w') as f:
            try:
                json_obiekt = json.load(f)
            except Exception:
                x = '{ "dimensions": { "x":500, "y":500,"width":500,"height":500}}'
                json_obiekt = json.loads(x)
            json.dump(json_obiekt, f, indent=4)


def set_current_page(last_page_index):
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            json_obiekt = json.load(f)
            json_obiekt["last_page_index"] = last_page_index
        print(json_obiekt)
        with open(FILE_NAME, 'w') as f:
            json.dump(json_obiekt, f, indent=4)


def get_last_page():
    with open('settings.json', 'r') as f:
        json_obiekt = json.load(f)
    return json_obiekt['last_page_index']


def get_dimension():
    with open('settings.json', 'r') as f:
        json_obiekt = json.load(f)
        dim = json_obiekt['dimensions']
    return dim['x'], dim['y'], dim['width'], dim['height']


def get_json_value(name: str) -> str:
    with open('settings.json', 'r') as f:
        json_obiekt = json.load(f)
        dim = json_obiekt[name]
    return dim


def set_json_value(*, name: str, name2: str, value: str) -> None:
    json_obiekt = ''
    with open(FILE_NAME, 'r') as f:
        json_obiekt = json.load(f)
        json_obiekt[name][name2] = value
    with open(FILE_NAME, 'w') as f:
        json.dump(json_obiekt, f, indent=4)
    return


def set_display_value(*, index: int, bool_value: bool) -> None:
    # 0 - Ang, 1 - Pol, 2 - Feq, 3 - Badly, 4 Perfect
    columns = ["Angielski", "Polski", "Frequency",
               "BadlyAnswer", "PerfectScore"]
    name = columns[index]
    json_obiekt = ''
    with open(FILE_NAME, 'r') as f:
        json_obiekt = json.load(f)
        json_obiekt['display_columns_configurations'][name] = bool_value
    with open(FILE_NAME, 'w') as f:
        json.dump(json_obiekt, f, indent=4)
    return


def get_display_value(index: int) -> str:
    columns = ["Angielski", "Polski", "Frequency",
               "BadlyAnswer", "PerfectScore"]
    name = columns[index]
    with open('settings.json', 'r') as f:
        json_obiekt = json.load(f)
        value = json_obiekt['display_columns_configurations'][name]
    return value
