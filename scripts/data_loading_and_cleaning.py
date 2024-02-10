import pandas as pd
import re
import math

def load_csv_data(file_path):
    """
    Loads a CSV file into a pandas DataFrame.
    """
    return pd.read_csv(file_path)

def clean_content(content):
    """
    Removes square bracketed content from a string.
    """
    if isinstance(content, str):
        return re.sub(r'\[[^\]]+\]', '', content)
    return content

def replace_range_with_mean(cell):
    """
    Replaces a range (e.g., "10-20") with its mean (e.g., "15").
    """
    parts = str(cell).split('-')
    if len(parts) == 2:
        try:
            low, high = map(int, parts)
            return math.ceil((low + high) / 2)
        except ValueError:
            return cell
    return cell