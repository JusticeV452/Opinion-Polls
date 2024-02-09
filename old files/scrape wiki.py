from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import wikipedia as wp
import re
import math
import os

# Function to clean cell content
def clean_content(content):
    if isinstance(content, str):
        return re.sub(r'\[[^\]]+\]', '', content)
    return content

# Function to replace range with mean
def replace_range_with_mean(cell):
    if isinstance(cell, str) and '-' in cell:
        # Split the cell by '-'
        parts = cell.split('-')

        # Check if there are exactly two parts, which represent a range
        if len(parts) == 2:
            try:
                low, high = map(int, parts)
                return math.ceil((low + high) / 2)
            except ValueError:
                return cell
    return cell

# Function to clean the DataFrame
def clean_dataframe(df):
    # Clean each cell in the DataFrame
    df = df.applymap(clean_content)

    # Find the actual name of the 'Margin of error' column, case-insensitively
    margin_of_error_col = next((col for col in df.columns if col.lower() == 'margin of error'), None)

    # Extract only numeric digits in the 'Margin of error' column if it exists
    if margin_of_error_col:
        df[margin_of_error_col] = df[margin_of_error_col].str.replace(r'\D', '', regex=True)

    return df

# Function to save a table as CSV
def save_table_as_csv(df, title, folder_name):
    # Clean the title
    cleaned_title = clean_content(title)

    # Clean the DataFrame
    df = clean_dataframe(df)

    sanitized_title = re.sub(r'[\\/:*?"<>|]', '', cleaned_title)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    csv_file_name = os.path.join(folder_name, f"{sanitized_title}.csv")
    df.to_csv(csv_file_name, index=False)
    print(f"Saved table as {csv_file_name}")

# Function to get tables from Wikipedia and process them
def get_and_process_tables():
    folder_name = "2024 election data"
    html = wp.page("Opinion_polling_for_the_next_Indian_general_election").html().encode("UTF-8")
    tables, table_titles = get_number_of_tables(html)

    for i, (table, title) in enumerate(zip(tables, table_titles)):
        df = pd.read_html(StringIO(str(table)), header=1)[0]
        df = df.applymap(replace_range_with_mean)
        print(f"Table Title: {title}")
        save_table_as_csv(df, title, folder_name)

# Function to get the number of tables from Wikipedia
def get_number_of_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.findAll("table", {"class": "wikitable"})
    table_titles = []

    for table in tables:
        caption_tag = table.find('caption')
        h3_tag = table.find_previous_sibling('h3')

        if caption_tag:
            table_titles.append(caption_tag.get_text().strip())
        elif h3_tag:
            table_titles.append(h3_tag.get_text().strip())
        else:
            table_titles.append("No Title")

    return tables, table_titles


if __name__ == "__main__":
    get_and_process_tables()
