import pandas as pd
import json
from config.data_paths import (
    base_data_path, 
    tags_data_path, 
    weapons_data_path
)

with open(base_data_path, 'r') as f:
    BASE_DATA = pd.read_csv(f)

with open(tags_data_path, 'r') as f:
    TAGS = json.load(f)

with open(weapons_data_path, 'r') as f:
    WEAPONS_DICT = json.load(f)

STAT_NAMES = ['Strength', 'Dexterity', 'Defense', 'Speed']
COMPARATORS = ['=', '<=', '>=', '<', '>', 'between']
