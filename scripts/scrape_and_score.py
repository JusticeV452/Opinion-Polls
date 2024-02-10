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

initial_data_path = 'data/Initial Data.csv'
predicted_skew_numbers_path = 'data/Predicted_Skew_Numbers_2023.csv'
pollsters_ranking_df_path = 'data/Final_Pollster_Rankings.csv'

# Read CSV files into pandas DataFrames
initial_data_df = pd.read_csv(initial_data_path)
predicted_skew_numbers_df = pd.read_csv(predicted_skew_numbers_path)
pollsters_ranking_df = pd.read_csv(pollsters_ranking_df_path)

# Clearing the terminal screen
os.system('clear')

def print_heading(message):
    print(f"\033[1;91m{message}\033[0m")

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

def clean_dataframe(state_data):
    state_data = state_data.apply(lambda x: x.map(clean_content))
    margin_of_error_col = next((col for col in state_data.columns if 'margin of error' in col.lower()), None)
    if margin_of_error_col:
        state_data[margin_of_error_col] = state_data[margin_of_error_col].str.replace(r'\D', '', regex=True)
    return state_data

def save_table_as_csv(state_data, title, folder_name="data/wikipedia_scrape"):
    cleaned_title = clean_content(title)
    sanitized_title = re.sub(r'[\\/:*?"<>|]', '', cleaned_title)
    directory = os.path.join(folder_name, sanitized_title + ".csv")
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    state_data.to_csv(directory, index=False)

def get_and_process_tables():
    html = wp.page("Opinion_polling_for_the_next_Indian_general_election").html().encode("UTF-8")
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.findAll("table", {"class": "wikitable"})
    table_titles = [table.find('caption').get_text().strip() if table.find('caption') else "No Title" for table in tables]

    
    for table, title in zip(tables, table_titles):
        if title != "No Title":
            state_data = pd.read_html(StringIO(str(table)), header=1)[0]
            state_data = state_data.apply(lambda x: x.map(replace_range_with_mean))
            state_data['Date published'] = state_data['Date published'].str.replace(r'\[\d+\]', '', regex=True)
            
            if 'Sample size' in state_data.columns:
                state_data['Sample size'] = state_data['Sample size'].str.replace('[^\d]', '', regex=True).astype(int)
            save_table_as_csv(state_data, title)

def generate_seat_projections():

    seat_projections_path = "data/wikipedia_scrape/Seat Projections.csv"
    
    seat_projections = pd.read_csv(seat_projections_path)
    global pollsters_ranking_df, predicted_skew_numbers_df, initial_data_df  # Using global variables for hardcoded data

    if seat_projections.isnull().any().any() or pollsters_ranking_df.isnull().any().any() or predicted_skew_numbers_df.isnull().any().any():
        raise ValueError("Missing data in one or more DataFrames. Please check your data files.")

    # Error handling: Check for required columns in the DataFrames
    required_columns_seat_projections = ['Polling agency', 'Date published', 'Sample size', 'Margin of Error', 'NDA', 'I.N.D.I.A.', 'Others']
    for col in required_columns_seat_projections:
        if col not in seat_projections.columns:
            raise ValueError(f"Missing required column '{col}' in the seat_projections DataFrame.")

    # Error handling: Check for validity of date formats
    try:
        seat_projections['Date published'] = seat_projections['Date published'].str.replace('\[\d+\]', '', regex=True)
        seat_projections['Date published'] = pd.to_datetime('15 ' + seat_projections['Date published'], format='%d %B %Y')  
        
    except Exception as e:
        raise ValueError(f"Invalid date format in 'Date published' column. Please ensure the dates are correctly formatted. {e}")

    # Apply dynamic skew adjustments
    for party in predicted_skew_numbers_df['Party']:
        skew_adjustment = predicted_skew_numbers_df.loc[predicted_skew_numbers_df['Party'] == party, 'Adjusted Seat Skew'].values[0]
        if party in seat_projections.columns:
            seat_projections[party] = seat_projections[party] + skew_adjustment

    # Load initial values for WMA calculation from "Initial Data.csv"
    initial_nda = initial_data_df.loc[initial_data_df['Party'] == 'NDA', 'Seat Projection'].values[0]
    initial_india = initial_data_df.loc[initial_data_df['Party'] == 'I.N.D.I.A.', 'Seat Projection'].values[0]
    initial_others = initial_data_df.loc[initial_data_df['Party'] == 'Others', 'Seat Projection'].values[0]

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
        ranking = pollsters_ranking_df[pollsters_ranking_df['Polling agency'] == agency]['Ranking'].values
        return ranking[0] if len(ranking) > 0 else 0.95
    seat_projections['Polling Agency Quality Score'] = [np.mean([calculate_quality_score(agency.strip()) for agency in agencies.split('-')]) for agencies in seat_projections['Polling agency']]

    # Now calculate the median
    max_sample_size = (seat_projections['Sample size'].max())
    min_sample_size = (seat_projections['Sample size'].min())

    # Calculate the scaling factor
    scaling_factor = (1.5 - 0.5) / (max_sample_size - min_sample_size)

    # Calculate and apply the Sample Size Score with the correct scaling
    seat_projections['Sample Size Score'] = seat_projections['Sample size'].apply(lambda x: 0.5 + scaling_factor * (x - min_sample_size))

    # Calculate Margin of Error Score
    seat_projections['Margin of Error'] = seat_projections['Margin of Error'].str.replace('[^\d]', '', regex=True).astype(float)
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
    output_csv_filename = 'data/wikipedia_scrape/WMA_Seat_Projections.csv'
    directory = os.path.dirname(output_csv_filename)
    if directory and not os.path.exists(directory): os.makedirs(directory)
    seat_projections.to_csv(output_csv_filename, index=False)
    print(f'Seat Projections Generated, Saved to {output_csv_filename}')

def run_tableau_flow(flow_file_path):
    # Full path to tableau-prep-cli
    TABLEAU_PREP_CLI_PATH = '/Applications/Tableau Prep Builder 2023.3.app/Contents/scripts/tableau-prep-cli'

    if not os.path.exists(TABLEAU_PREP_CLI_PATH):
        print("Error: Tableau Prep CLI does not exist at the specified path.")
        return

    if not os.path.exists(flow_file_path):
        print("Error: Flow file does not exist at the specified path.")
        return

    try:
        subprocess.run([TABLEAU_PREP_CLI_PATH, "-t", flow_file_path], check=True)
        print("Tableau Flow executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Tableau Flow execution: {e}")
        exit()

def process_state_data():
    # Assuming the Tableau flow has already processed the data and saved it to a CSV file
    csv_file_path = "data/Combined States Data.csv"

    # Check if the processed CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: Processed state data file does not exist at {csv_file_path}.")
        return

    # Read the processed state data CSV file
    state_data = pd.read_csv(csv_file_path)

    # Identify columns representing parties or candidates
    state_data['Date published'] = pd.to_datetime(state_data['Date published'], errors='coerce')

    # Calculate the difference in days between the publication date and the latest date for each state
    state_data['Days Difference'] = state_data.groupby('States')['Date published'].transform(lambda x: (x.max() - x).dt.days)

    # Get the columns that represent parties dynamically
    party_columns = [col for col in state_data.columns if col not in ['States', 'Polling agency', 'Date published', 'Days Difference']]

    # Convert party columns to numeric
    state_data[party_columns] = state_data[party_columns].apply(pd.to_numeric, errors='coerce')

    # Create a DataFrame to store party scores
    party_scores = state_data[['States']].copy()

    # Calculate weighted scores for each party based on recency and add to party_scores DataFrame
    for party in party_columns:
        party_scores[party] = state_data[party] * state_data['Days Difference']

    # Group by State to get the final result
    party_scores = party_scores.groupby('States').sum()  # Sum up the scores for each party in each state

    # Find the party with the maximum weighted score for each state
    party_scores['Leading Party'] = party_scores[party_columns].idxmax(axis=1)

    # Reset the index to match your desired output format
    result = party_scores.reset_index()

    # Save the result to a CSV file
    output_file = 'data/wikipedia_scrape/Leading_Party_By_State.csv'
    directory = os.path.dirname(output_file)
    if directory and not os.path.exists(directory): os.makedirs(directory)
    result.to_csv(output_file, index=False)
    print(f"State Results Generated,  Saved to {output_file}")

def main():
    print_heading("Starting Scraping Process...")
    get_and_process_tables()
    print('Scraping Finished.')

    print_heading("Generating Projections...")
    generate_seat_projections()

    print_heading("Generating State Data...")
    process_state_data()

if __name__ == "__main__":
    main()
