# Importing necessary libraries for all scripts
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import wikipedia as wp
import re
import math
import os
import numpy as np
from datetime import datetime
import subprocess

os.system('clear')
# Hard-coded data
initial_data = [{'Party': 'NDA', 'Seat Projection': 348, 'Vote Share': 38}, {'Party': 'I.N.D.I.A.', 'Seat Projection': 142, 'Vote Share': 40}, {'Party': 'Others', 'Seat Projection': 53, 'Vote Share': 22}, {'Party': 'Total', 'Seat Projection': 543, 'Vote Share': 100}]
predicted_skew_numbers = [{'Party': 'NDA', 'Seat Projection Skew': 28.5979798, 'Vote Share Projection Skew': 5.15, 'Adjusted Seat Skew': 9.532659933, 'Adjusted Vote Share Skew': 1.716666667}, {'Party': 'I.N.D.I.A.', 'Seat Projection Skew': -17.25858586, 'Vote Share Projection Skew': -3.13, 'Adjusted Seat Skew': -5.752861953, 'Adjusted Vote Share Skew': -1.043333333}, {'Party': 'Others', 'Seat Projection Skew': 0.0, 'Vote Share Projection Skew': 0.0, 'Adjusted Seat Skew': 0.0, 'Adjusted Vote Share Skew': 0.0}]
pollster_rankings = [{'Polling agency': 'VDP Associates', 'Ranking': 0.75}, {'Polling agency': 'The Week', 'Ranking': 0.761792458}, {'Polling agency': 'Times Now', 'Ranking': 0.843019385}, {'Polling agency': 'CVoter', 'Ranking': 0.875914609}, {'Polling agency': 'India Today', 'Ranking': 0.915754503}, {'Polling agency': 'ABP News', 'Ranking': 0.926869819}, {'Polling agency': 'Karvy', 'Ranking': 0.940594155}, {'Polling agency': 'Zee 24 Taas', 'Ranking': 0.945253385}, {'Polling agency': 'Nielsen', 'Ranking': 0.951169625}, {'Polling agency': 'CSDS', 'Ranking': 1.011886139}, {'Polling agency': 'CNN-IBN', 'Ranking': 1.013901558}, {'Polling agency': 'News Nation', 'Ranking': 1.031826435}, {'Polling agency': 'VMR', 'Ranking': 1.033332305}, {'Polling agency': 'India TV', 'Ranking': 1.041889898}, {'Polling agency': 'Hansa Research', 'Ranking': 1.087264153}, {'Polling agency': 'CNX', 'Ranking': 1.109806368}, {'Polling agency': 'Lokniti', 'Ranking': 1.118134252}, {'Polling agency': 'NDTV', 'Ranking': 1.25}]

# --- Start of Scraping Process ---
print("\033[1;91mStarting Scraping Process...\033[0m")

# Function to clean cell content
def clean_content(content):
    if isinstance(content, str):
        return re.sub(r'\[[^\]]+\]', '', content)
    return content

# Function to replace range with mean
import re

def replace_range_with_mean(cell):
    if re.match(r'\d+-\d+', str(cell)):
        parts = cell.split('-')
        low, high = map(int, parts)
        return math.ceil((low + high) / 2)
    else:
        return cell
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
    df = df.apply(lambda x: x.map(clean_content))

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
    csv_file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name, f"{sanitized_title}.csv")
    directory = os.path.dirname(csv_file_name)
    if directory and not os.path.exists(directory): os.makedirs(directory)
    df.to_csv(csv_file_name, index=False)
    

# Function to get tables from Wikipedia and process them
def get_and_process_tables():
    folder_name = "2024 election data"
    html = wp.page("Opinion_polling_for_the_next_Indian_general_election").html().encode("UTF-8")
    tables, table_titles = get_number_of_tables(html)

    for i, (table, title) in enumerate(zip(tables, table_titles)):
        df = pd.read_html(StringIO(str(table)), header=1)[0]
        df = df.apply(lambda x: x.map(replace_range_with_mean))
        
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

print('Scraping Finished')

# --- Run Algorithm to Generate Seat Projections ---

print("\033[1;91mGenerating Projections...\033[0m")

# Load the raw data files


# Get the current working directory
cwd = os.getcwd()

# Define the relative path to your file
relative_path = "python scripts/scrape wikipedia/2024 election data/Seat Projections.csv"

# Combine the current working directory with the relative path
seat_projections_path = os.path.join(cwd, relative_path)

if not os.path.exists(seat_projections_path): raise FileNotFoundError("seat_projections_path does not exist.")
seat_projections = pd.read_csv(seat_projections_path)

# Error handling: Check for missing data in the DataFrames

# Explicitly converting to DataFrames if they are lists
if isinstance(seat_projections, list):
    seat_projections = pd.DataFrame(seat_projections)
if isinstance(pollster_rankings, list):
    pollster_rankings = pd.DataFrame(pollster_rankings)
if isinstance(predicted_skew_numbers, list):
    predicted_skew_numbers = pd.DataFrame(predicted_skew_numbers)

if seat_projections.isnull().values.any() or pollster_rankings.isnull().values.any() or predicted_skew_numbers.isnull().values.any():
    raise ValueError("Missing data in one or more DataFrames. Please check your data files.")

# Error handling: Check for required columns in the DataFrames
required_columns_seat_projections = ['Polling agency', 'Date published', 'Sample size', 'Margin of Error', 'NDA', 'I.N.D.I.A.', 'Others']
for col in required_columns_seat_projections:
    if col not in seat_projections.columns:
        raise ValueError(f"Missing required column '{col}' in the seat_projections DataFrame.")

# Error handling: Check for validity of date formats
try:
    seat_projections['Date published'] = pd.to_datetime('15 ' + seat_projections['Date published'], format='%d %B %Y')
except Exception as e:
    raise ValueError("Invalid date format in 'Date published' column. Please ensure the dates are correctly formatted.")

# Apply dynamic skew adjustments
for party in predicted_skew_numbers['Party']:
    skew_adjustment = predicted_skew_numbers.loc[predicted_skew_numbers['Party'] == party, 'Adjusted Seat Skew'].values[0]
    if party in seat_projections.columns:
        seat_projections[party] = seat_projections[party] + skew_adjustment

# Load initial values for WMA calculation from "Initial Data.csv"

# Using hard-coded data to set initial seat projections
initial_nda = next(item['Seat Projection'] for item in initial_data if item['Party'] == 'NDA')
initial_india = next(item['Seat Projection'] for item in initial_data if item['Party'] == 'I.N.D.I.A.')
initial_others = next(item['Seat Projection'] for item in initial_data if item['Party'] == 'Others')

# Calculate days to election
election_date = datetime.strptime('2024-06-01', '%Y-%m-%d')
seat_projections['Date published'] = pd.to_datetime(seat_projections['Date published'])
seat_projections['Days to Election'] = (election_date - seat_projections['Date published']).dt.days

# Disaggregate combined polling agencies in the seat projection data
disaggregated_agencies = []
for combined_agency in seat_projections['Polling agency']:
    agencies = combined_agency.split('-')
    disaggregated_agencies.extend(agencies)

# Calculate the Polling Agency Quality Score
def calculate_quality_score(agency):
    # Find the agency in the rankings file, or assign a default value of 0.95 if not found
    ranking = pollster_rankings[pollster_rankings['Polling agency'] == agency]['Ranking'].values
    return ranking[0] if len(ranking) > 0 else 0.95
seat_projections['Polling Agency Quality Score'] = [np.mean([calculate_quality_score(agency.strip()) for agency in agencies.split('-')]) for agencies in seat_projections['Polling agency']]

# Calculate Sample Size Score
# Replace commas and convert to numeric
seat_projections['Sample size'] = pd.to_numeric(seat_projections['Sample size'].str.replace(',', ''))

# Now calculate the median
median_sample_size = seat_projections['Sample size'].median()
max_sample_size = seat_projections['Sample size'].max()
min_sample_size = seat_projections['Sample size'].min()

# Calculate the scaling factor
scaling_factor = (1.5 - 0.5) / (max_sample_size - min_sample_size)

# Calculate and apply the Sample Size Score with the correct scaling
seat_projections['Sample Size Score'] = seat_projections['Sample size'].apply(lambda x: 0.5 + scaling_factor * (x - min_sample_size))

# Calculate Margin of Error Score
median_margin_of_error = seat_projections['Margin of Error'].median()
seat_projections['Margin of Error Score'] = seat_projections['Margin of Error'].apply(lambda x: 0.5 + 1 * (median_margin_of_error - x) / median_margin_of_error)

# Calculate Recency Score
max_days_to_election = seat_projections['Days to Election'].max()
seat_projections['Recency Score'] = seat_projections['Days to Election'].apply(lambda x: 0.5 + (max_days_to_election - x) / max_days_to_election)

# Calculate Overall Poll Quality
seat_projections['Overall Poll Quality'] = 0.4 * seat_projections['Recency Score'] + 0.25 * seat_projections['Polling Agency Quality Score'] + 0.3 * seat_projections['Sample Size Score'] + 0.05 * seat_projections['Margin of Error Score']

# Initialize WMA with initial values
wma_nda = initial_nda
wma_india = initial_india
wma_others = initial_others

# Sort DataFrame by 'Days to Election' for WMA calculation
seat_projections.sort_values(by='Days to Election', ascending=False, inplace=True)
seat_projections.reset_index(drop=True, inplace=True)

# Calculate WMA
for i, row in seat_projections.iterrows():
    weight = row['Overall Poll Quality']
    if np.isnan(weight):
        continue
    wma_nda = (wma_nda * (i) + row['NDA'] * weight) / (i + weight)
    wma_india = (wma_india * (i) + row['I.N.D.I.A.'] * weight) / (i + weight)
    wma_others = (wma_others * (i) + row['Others'] * weight) / (i + weight)
    
    #scale wma to fit 543
    total_seats = wma_nda + wma_india + wma_others
    scaling_factor = 543 / total_seats
    
    wma_nda_scaled = wma_nda * scaling_factor
    wma_india_scaled = wma_india * scaling_factor
    wma_others_scaled = wma_others * scaling_factor
    
    wma_nda_rounded = int(round(wma_nda_scaled))
    wma_india_rounded = int(round(wma_india_scaled))
    wma_others_rounded = int(round(wma_others_scaled))
    
    seat_projections.loc[i, 'WMA_NDA_Rounded'] = wma_nda_rounded
    seat_projections.loc[i, 'WMA_INDIA_Rounded'] = wma_india_rounded
    seat_projections.loc[i, 'WMA_Others_Rounded'] = wma_others_rounded

# Save the DataFrame to a CSV file
output_csv_filename = '2024 election data/WMA_Seat_Projections.csv'
directory = os.path.dirname(output_csv_filename)
if directory and not os.path.exists(directory): os.makedirs(directory)
seat_projections.to_csv(output_csv_filename, index=False)

# Full path to tableau-prep-cli
tableau_prep_cli_path = '/Applications/Tableau Prep Builder 2022.3.app/Contents/scripts/tableau-prep-cli'

# Run the Tableau Flow and wait for it to complete
flow_file_path = os.path.join(cwd, relative_path)

# Check if Tableau Prep CLI exists
if not os.path.exists(tableau_prep_cli_path):
    print("Error: Tableau Prep CLI does not exist at the specified path.")
else:
    # Check if the flow file exists
    if not os.path.exists(flow_file_path):
        print("Error: Flow file does not exist at the specified path.")
    else:
        # Run the Tableau Flow and wait for it to complete
        try:
            subprocess.run([tableau_prep_cli_path, "-t", flow_file_path], check=True)
            print("Tableau Flow executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Tableau Flow execution: {e}")
            exit()
print('Projections Generated.')

# --- Process State-by-State Data ---

print("\033[1;91mGenerating State Data...\033[0m")

# Run the Tableau Flow and wait for it to complete
flow_file_path = 'Clean_State_Data.tfl'  # Adjust this path as needed

# Check if Tableau Prep CLI exists
if not os.path.exists(tableau_prep_cli_path):
    print("Error: Tableau Prep CLI does not exist at the specified path.")
else:
    # Check if the flow file exists
    if not os.path.exists(flow_file_path):
        print("Error: Flow file does not exist at the specified path.")
    else:
        # Run the Tableau Flow and wait for it to complete
        try:
            subprocess.run([tableau_prep_cli_path, "-t", flow_file_path], check=True)
            print("Tableau Flow executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Tableau Flow execution: {e}")

# Define the relative path to your file
relative_path = "python scripts/scrape wikipedia/Algorithm Output/Combined States Data.csv"

# Combine the current working directory with the relative path
file_location = os.path.join(cwd, relative_path)

if not os.path.exists(file_location): raise FileNotFoundError("file_location does not exist.")
df = pd.read_csv(file_location)

# Clean the 'Date published' field with inferred date format
df['Date published'] = pd.to_datetime(df['Date published'], errors='coerce')

# Calculate the difference in days between the publication date and the latest date for each state
df['Days Difference'] = df.groupby('States')['Date published'].transform(lambda x: (x.max() - x).dt.days)

# Get the columns that represent parties dynamically
party_columns = [col for col in df.columns if col not in ['States', 'Polling agency', 'Date published', 'Days Difference']]

# Convert party columns to numeric
df[party_columns] = df[party_columns].apply(pd.to_numeric, errors='coerce')

# Create a DataFrame to store party scores
party_scores = df[['States']].copy()

# Calculate weighted scores for each party based on recency and add to party_scores DataFrame
for party in party_columns:
    party_scores[party] = df[party] * df['Days Difference']

# Group by State to get the final result
party_scores = party_scores.groupby('States').sum()  # Sum up the scores for each party in each state

# Find the party with the maximum weighted score for each state
party_scores['Leading Party'] = party_scores[party_columns].idxmax(axis=1)

# Reset the index to match your desired output format
result = party_scores.reset_index()

# Save the result to a CSV file
output_file = 'Algorithm Output/Leading_Party_By_State.csv'
directory = os.path.dirname(output_file)
if directory and not os.path.exists(directory): os.makedirs(directory)
result.to_csv(output_file, index=False)
print('State Results Generated')

print(f"Result saved to '{output_file}'")