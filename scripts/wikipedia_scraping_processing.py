from bs4 import BeautifulSoup
import wikipedia as wp
from io import StringIO
import pandas as pd
import os
from data_loading_and_cleaning import clean_content, replace_range_with_mean
import re

def save_table_as_csv(state_data, title, folder_name="data/wikipedia_scrape"):
    cleaned_title = clean_content(title)
    sanitized_title = re.sub(r'[\\/:*?"<>|]', '', cleaned_title)
    directory = os.path.join(folder_name, sanitized_title + ".csv")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    state_data.to_csv(directory, index=False)

def get_and_process_tables():
    page = wp.page("Opinion_polling_for_the_next_Indian_general_election")
    html_content = page.html()
    soup = BeautifulSoup(html_content, 'html.parser')

    sections_of_interest = [
        "Vote Share Projections",
        "Seat Projections",
    ]

    states_and_uts = [
        "Andaman and Nicobar Islands (01)", "Andhra Pradesh (25)", "Arunachal Pradesh (02)",
        "Assam (14)", "Bihar (40)", "Chandigarh (01)", "Chhattisgarh (11)",
        "Dadra and Nagar Haveli and Daman and Diu (02)", "Delhi (07)", "Goa (02)",
        "Gujarat (26)", "Haryana (10)", "Himachal Pradesh (04)", "Jammu and Kashmir (05)",
        "Jharkhand (14)", "Karnataka (28)", "Kerala (20)", "Ladakh (01)",
        "Lakshadweep (01)", "Madhya Pradesh (29)", "Maharashtra (48)", "Manipur (02)",
        "Meghalaya (02)", "Mizoram (01)", "Nagaland (01)", "Odisha (21)",
        "Puducherry (01)", "Punjab (13)", "Rajasthan (25)", "Sikkim (01)",
        "Tamil Nadu (39)", "Telangana (17)", "Tripura (02)", "Uttar Pradesh (80)",
        "Uttarakhand (05)", "West Bengal (42)"
    ]

    sections_of_interest.extend(states_and_uts)

    for section in sections_of_interest:
        heading = soup.find(id=section.replace(" ", "_").replace("&", "and"))
        if heading:
            table = heading.find_next("table", {"class": "wikitable"})
        else:
            tables = soup.find_all('table', {'class': 'wikitable'})
            for t in tables:
                caption = t.find('caption')
                if caption and caption.get_text().strip() == section:
                    table = t
                    break
            else:
                continue

        df = pd.read_html(StringIO(str(table)), header=1)[0]
        df = df.apply(lambda x: x.map(replace_range_with_mean))
        df['Date published'] = df['Date published'].str.replace(r'\[\d+\]', '', regex=True)
        if 'Sample size' in df.columns:
            df['Sample size'] = df['Sample size'].str.replace(r'\[\d+\]', '', regex=True).str.replace(',', '').astype(int)
        save_table_as_csv(df, section)
        # Inside the for loop of get_and_process_tables, after save_table_as_csv:
        print(f"Processed and saved table: {section}")