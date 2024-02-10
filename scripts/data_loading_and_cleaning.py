import pandas as pd
import re
import math

def load_csv_data(file_path):
    return pd.read_csv(file_path)

def clean_content(content):
    if isinstance(content, str):
        return re.sub(r'\[[^\]]+\]', '', content)
    return content

def replace_range_with_mean(cell):
    parts = str(cell).split('-')
    if len(parts) == 2:
        try:
            low, high = map(int, parts)
            return math.ceil((low + high) / 2)
        except ValueError:
            return cell
    return cell
