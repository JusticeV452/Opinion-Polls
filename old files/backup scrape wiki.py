from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import wikipedia as wp
import re
import math
import os

def clean_content(content):
    if isinstance(content, str):
        return re.sub(r'\[[^\]]+\]', '', content)
    return content

def replace_range_with_mean(cell):
    if isinstance(cell, str) and '-' in cell:
        try:
            low, high = map(int, cell.split('-'))
            return math.ceil((low + high) / 2)
        except ValueError:
            return cell
    return cell

def clean_dataframe(df):
    # Clean each cell in the DataFrame
    df = df.apply(lambda col: col.map(clean_content), axis='index')
    
    # Find the actual name of the 'Margin of error' column, case-insensitively
    margin_of_error_col = next((col for col in df.columns if col.lower() == 'margin of error'), None)
    
    # Extract only numeric digits in the 'Margin of error' column if it exists
    if margin_of_error_col:
        df[margin_of_error_col] = df[margin_of_error_col].str.replace(r'\D', '', regex=True)
    
    return df

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

def main():
    folder_name = "2024 election data"
    html = wp.page("Opinion_polling_for_the_next_Indian_general_election").html().encode("UTF-8")
    tables, table_titles = get_number_of_tables(html)
    
    for i, (table, title) in enumerate(zip(tables, table_titles)):
        try:
            df = pd.read_html(StringIO(str(table)), header=1)[0]
            df = df.apply(lambda col: col.map(replace_range_with_mean), axis='index')
            print(f"Table Title: {title}")
            save_table_as_csv(df, title, folder_name)
        except IndexError:
            df = pd.read_html(StringIO(str(tables[0])), header=1)[0]
            df = df.apply(lambda col: col.map(replace_range_with_mean), axis='index')
            print(f"Table Title: {table_titles[0]}")
            save_table_as_csv(df, table_titles[0], folder_name)
        except Exception as e:
            print(f"Error processing table {i}: {e}")

if __name__ == "__main__":
    main()
