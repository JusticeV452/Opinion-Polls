import pandas as pd
import numpy as np
from datetime import datetime
import os
from calculate_poll_quality import calculate_scores

# Constants
INITIAL_DATA_PATH = 'data/constant_initial_data/Initial_Data.csv'
PREDICTED_SKEW_NUMBERS_PATH = 'data/constant_initial_data/Predicted_Skew_Numbers_2023.csv'
SEAT_PROJECTIONS_PATH = "data/wikipedia_scrape/Seat Projections.csv"
OUTPUT_CSV_FILENAME = 'data/script_outputs/polls_moving_averages.csv'

# Load initial data
initial_data_df = pd.read_csv(INITIAL_DATA_PATH)
predicted_skew_numbers_df = pd.read_csv(PREDICTED_SKEW_NUMBERS_PATH)

def validate_data(seat_projections):
    required_columns = ['Polling agency', 'Date published', 'Sample size', 'Margin of Error', 'NDA', 'I.N.D.I.A.', 'Others']
    if not all(column in seat_projections.columns for column in required_columns):
        missing_columns = [column for column in required_columns if column not in seat_projections.columns]
        raise ValueError(f"Missing required columns: {missing_columns}")
    if seat_projections.isnull().any().any():
        raise ValueError("Missing data in the seat_projections DataFrame.")

def clean_and_prepare_seat_projections(seat_projections):
    validate_data(seat_projections)

    seat_projections['Date published'] = seat_projections['Date published'].str.replace('\[\d+\]', '', regex=True)
    seat_projections['Date published'] = pd.to_datetime('15 ' + seat_projections['Date published'], format='%d %B %Y', errors='coerce')
    
    seat_projections['Margin of Error'] = seat_projections['Margin of Error'].str.replace('[^\d]', '', regex=True).astype(float)
    seat_projections['Sample size'] = seat_projections['Sample size'].astype(str).str.replace(',', '').astype(int)
    election_date = datetime.strptime('2024-06-01', '%Y-%m-%d')
    seat_projections['Days to Election'] = (election_date - seat_projections['Date published']).dt.days

def apply_skew_adjustments(seat_projections):
    for party in predicted_skew_numbers_df['Party']:
        skew_adjustment = predicted_skew_numbers_df.loc[predicted_skew_numbers_df['Party'] == party, 'Adjusted Seat Skew'].values[0]
        if party in seat_projections.columns:
            seat_projections[party] += skew_adjustment

def calculate_weighted_moving_averages(seat_projections):
    initial_values = {party: initial_data_df.loc[initial_data_df['Party'] == party, 'Seat Projection'].values[0] for party in ['NDA', 'I.N.D.I.A.', 'Others']}
    wma = initial_values.copy()

    seat_projections.sort_values(by='Days to Election', ascending=False, inplace=True)
    seat_projections.reset_index(drop=True, inplace=True)

    for i, row in seat_projections.iterrows():
        weight = row['Overall Poll Quality']
        if np.isnan(weight):
            continue
        for party in wma.keys():
            wma[party] = (wma[party] * i + row[party] * weight) / (i + weight)

        total_seats = sum(wma.values())
        scaling_factor = 543 / total_seats

        for party in wma.keys():
            wma_scaled = wma[party] * scaling_factor
            seat_projections.loc[i, f'{party}_Moving_Average'] = int(round(wma_scaled))

def save_to_csv(seat_projections):
    directory = os.path.dirname(OUTPUT_CSV_FILENAME)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    seat_projections.to_csv(OUTPUT_CSV_FILENAME, index=False)
    print(f'Seat Projections Generated, Saved to {OUTPUT_CSV_FILENAME}')

def generate_seat_projections():
    seat_projections = pd.read_csv(SEAT_PROJECTIONS_PATH)
    
    clean_and_prepare_seat_projections(seat_projections)
    
    apply_skew_adjustments(seat_projections)
    
    calculate_scores(seat_projections)
    
    calculate_weighted_moving_averages(seat_projections)
    
    save_to_csv(seat_projections)

if __name__ == "__main__":
    generate_seat_projections()