import pandas as pd
import numpy as np
from datetime import datetime
from data_loading_and_cleaning import load_csv_data
import os

initial_data_path = 'data/constant_initial_data/Initial_Data.csv'
predicted_skew_numbers_path = 'data/constant_initial_data/Predicted_Skew_Numbers_2023.csv'
pollsters_ranking_df_path = 'data/constant_initial_data/Final_Pollster_Rankings.csv'

initial_data_df = load_csv_data(initial_data_path)
predicted_skew_numbers_df = load_csv_data(predicted_skew_numbers_path)
pollsters_ranking_df = load_csv_data(pollsters_ranking_df_path)

def generate_seat_projections():
    seat_projections_path = "data/wikipedia_scrape/Seat Projections.csv"
    seat_projections = load_csv_data(seat_projections_path)

    if seat_projections.isnull().any().any() or pollsters_ranking_df.isnull().any().any() or predicted_skew_numbers_df.isnull().any().any():
        raise ValueError("Missing data in one or more DataFrames. Please check your data files.")

    required_columns_seat_projections = ['Polling agency', 'Date published', 'Sample size', 'Margin of Error', 'NDA', 'I.N.D.I.A.', 'Others']
    for col in required_columns_seat_projections:
        if col not in seat_projections.columns:
            raise ValueError(f"Missing required column '{col}' in the seat_projections DataFrame.")

    try:
        seat_projections['Date published'] = seat_projections['Date published'].str.replace('\[\d+\]', '', regex=True)
        seat_projections['Date published'] = pd.to_datetime('15 ' + seat_projections['Date published'], format='%d %B %Y')
    except Exception as e:
        raise ValueError(f"Invalid date format in 'Date published' column. Please ensure the dates are correctly formatted. {e}")

    for party in predicted_skew_numbers_df['Party']:
        skew_adjustment = predicted_skew_numbers_df.loc[predicted_skew_numbers_df['Party'] == party, 'Adjusted Seat Skew'].values[0]
        if party in seat_projections.columns:
            seat_projections[party] = seat_projections[party] + skew_adjustment

    initial_nda = initial_data_df.loc[initial_data_df['Party'] == 'NDA', 'Seat Projection'].values[0]
    initial_india = initial_data_df.loc[initial_data_df['Party'] == 'I.N.D.I.A.', 'Seat Projection'].values[0]
    initial_others = initial_data_df.loc[initial_data_df['Party'] == 'Others', 'Seat Projection'].values[0]

    election_date = datetime.strptime('2024-06-01', '%Y-%m-%d')
    seat_projections['Date published'] = pd.to_datetime(seat_projections['Date published'])
    seat_projections['Days to Election'] = (election_date - seat_projections['Date published']).dt.days

    disaggregated_agencies = []
    for combined_agency in seat_projections['Polling agency']:
        agencies = combined_agency.split('-')
        disaggregated_agencies.extend(agencies)

    seat_projections['Polling Agency Quality Score'] = [
        np.mean([
            pollsters_ranking_df[pollsters_ranking_df['Polling agency'] == agency.strip()]['Ranking'].values[0] if len(pollsters_ranking_df[pollsters_ranking_df['Polling agency'] == agency.strip()]['Ranking'].values) > 0 else 0.95
            for agency in agencies.split('-')
        ])
        for agencies in seat_projections['Polling agency']
    ]

    max_sample_size = (seat_projections['Sample size'].max())
    min_sample_size = (seat_projections['Sample size'].min())
    scaling_factor = (1.5 - 0.5) / (max_sample_size - min_sample_size)
    seat_projections['Sample Size Score'] = seat_projections['Sample size'].apply(lambda x: 0.5 + scaling_factor * (x - min_sample_size))

    seat_projections['Margin of Error'] = seat_projections['Margin of Error'].str.replace('[^\d]', '', regex=True).astype(float)
    median_margin_of_error = seat_projections['Margin of Error'].median()
    seat_projections['Margin of Error Score'] = seat_projections['Margin of Error'].apply(lambda x: 0.5 + 1 * (median_margin_of_error - x) / median_margin_of_error)

    max_days_to_election = seat_projections['Days to Election'].max()
    seat_projections['Recency Score'] = seat_projections['Days to Election'].apply(lambda x: 0.5 + (max_days_to_election - x) / max_days_to_election)

    seat_projections['Overall Poll Quality'] = 0.4 * seat_projections['Recency Score'] + 0.25 * seat_projections['Polling Agency Quality Score'] + 0.3 * seat_projections['Sample Size Score'] + 0.05 * seat_projections['Margin of Error Score']

    wma_nda = initial_nda
    wma_india = initial_india
    wma_others = initial_others

    seat_projections.sort_values(by='Days to Election', ascending=False, inplace=True)
    seat_projections.reset_index(drop=True, inplace=True)

    for i, row in seat_projections.iterrows():
        weight = row['Overall Poll Quality']
        if np.isnan(weight):
            continue
        wma_nda = (wma_nda * (i) + row['NDA'] * weight) / (i + weight)
        wma_india = (wma_india * (i) + row['I.N.D.I.A.'] * weight) / (i + weight)
        wma_others = (wma_others * (i) + row['Others'] * weight) / (i + weight)
        
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
        

    seat_projections = seat_projections.rename(columns={
    'WMA_NDA_Rounded': 'NDA_Moving_Average',
    'WMA_INDIA_Rounded': 'INDIA_Moving_Average',
    'WMA_Others_Rounded': 'Others_Moving_Average'
    })
    
    output_csv_filename = 'data/script_outputs/polls_moving_averages.csv'
    directory = os.path.dirname(output_csv_filename)
    if directory and not os.path.exists(directory): os.makedirs(directory)
    seat_projections.to_csv(output_csv_filename, index=False)
    
    # At the end of generate_seat_projections function:
    print(f'Seat Projections Generated, Saved to {output_csv_filename}')