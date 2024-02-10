import pandas as pd
import numpy as np
from datetime import datetime

def load_data(paths):
    """Load data from the specified paths."""
    data_frames = {}
    for key, path in paths.items():
        data_frames[key] = pd.read_csv(path)
    return data_frames

def check_missing_data(data_frames):
    """Check for missing data in the DataFrames."""
    for df in data_frames.values():
        if df.isnull().values.any():
            raise ValueError("Missing data in one or more DataFrames. Please check your data files.")

def check_required_columns(data_frame, required_columns):
    """Check for required columns in the DataFrame."""
    for col in required_columns:
        if col not in data_frame.columns:
            raise ValueError(f"Missing required column '{col}'.")

def apply_dynamic_skew_adjustments(seat_projections, predicted_skew_numbers):
    """Apply dynamic skew adjustments to the seat projections."""
    for party in predicted_skew_numbers['Party']:
        skew_adjustment = predicted_skew_numbers.loc[predicted_skew_numbers['Party'] == party, 'Adjusted Seat Skew'].values[0]
        if party in seat_projections.columns:
            seat_projections[party] += skew_adjustment

def calculate_quality_score(pollster_rankings, agency):
    """Calculate the Polling Agency Quality Score."""
    ranking = pollster_rankings[pollster_rankings['Polling agency'] == agency]['Ranking'].values
    return ranking[0] if len(ranking) > 0 else 0.95

def calculate_scores(seat_projections, pollster_rankings):
    """Calculate various scores for the seat projections."""
    seat_projections['Polling Agency Quality Score'] = [np.mean([calculate_quality_score(pollster_rankings, agency.strip()) for agency in agencies.split('-')]) for agencies in seat_projections['Polling agency']]

    # Sample Size Score
    #median_sample_size = seat_projections['Sample size'].median()
    max_sample_size = seat_projections['Sample size'].max()
    min_sample_size = seat_projections['Sample size'].min()
    scaling_factor = (1.5 - 0.5) / (float(max_sample_size) - float(min_sample_size))    
    seat_projections['Sample Size Score'] = seat_projections['Sample size'].apply(lambda x: 0.5 + scaling_factor * (float(str(x).replace(',', '')) - float(str(min_sample_size).replace(',', '')))) 
    
    # Margin of Error Score
    seat_projections['Margin of Error'] = seat_projections['Margin of Error'].str.replace('[^\d]', '', regex=True).astype(float)
    median_margin_of_error = seat_projections['Margin of Error'].median()
    seat_projections['Margin of Error Score'] = seat_projections['Margin of Error'].apply(lambda x: 1 - (x / median_margin_of_error))
    
    # Recency Score
    election_date = datetime.strptime('2024-06-01', '%Y-%m-%d')
    seat_projections['Date published'] = pd.to_datetime(seat_projections['Date published'])
    seat_projections['Days to Election'] = (election_date - seat_projections['Date published']).dt.days
    
    max_days_to_election = seat_projections['Days to Election'].max()
    seat_projections['Recency Score'] = seat_projections['Days to Election'].apply(lambda x: 0.5 + (max_days_to_election - x) / max_days_to_election)
    
    # Overall Poll Quality
    seat_projections['Overall Poll Quality'] = 0.4 * seat_projections['Recency Score'] + 0.25 * seat_projections['Polling Agency Quality Score'] + 0.3 * seat_projections['Sample Size Score'] + 0.05 * seat_projections['Margin of Error Score']

def calculate_wma(seat_projections, initial_values):
    """Calculate the Weighted Moving Average (WMA) for seat projections."""
    initial_values_dict = initial_values.set_index('Party')['Seat Projection'].to_dict()
    wma_values = {party: initial_values_dict[party] for party in ['NDA', 'I.N.D.I.A.', 'Others']}

    for i, row in seat_projections.iterrows():
        weight = row['Overall Poll Quality']
        if np.isnan(weight):
            continue

        for party in wma_values.keys():
            wma_values[party] = (wma_values[party] * i + row[party] * weight) / (i + weight)

        total_seats = sum(wma_values.values())
        scaling_factor = 543 / total_seats

        for party in wma_values.keys():
            wma_values[party] = int(round(wma_values[party] * scaling_factor))
            seat_projections.loc[i, f'WMA_{party}_Rounded'] = wma_values[party]

def main():
    paths = {
        'seat_projections': "data/wikipedia_scrape/Seat Projections.csv",
        'pollster_rankings': "data/Final_Pollster_Rankings.csv",
        'predicted_skew_numbers': "data/Predicted_Skew_Numbers_2023.csv",
        'initial_values': "data/Initial Data.csv"
    }
    data_frames = load_data(paths)
    check_missing_data(data_frames)
    check_required_columns(data_frames['seat_projections'], ['Polling agency', 'Date published', 'Sample size', 'Margin of Error', 'NDA', 'I.N.D.I.A.', 'Others'])
    
    apply_dynamic_skew_adjustments(data_frames['seat_projections'], data_frames['predicted_skew_numbers'])
    
    calculate_scores(data_frames['seat_projections'], data_frames['pollster_rankings'])
    
    calculate_wma(data_frames['seat_projections'], data_frames['initial_values'])
    
    data_frames['seat_projections'].to_csv("WMA_Seat_Projections.csv", index=False)
    
    print(data_frames['seat_projections'].head())

if __name__ == "__main__":
    main()
