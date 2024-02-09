import pandas as pd
import numpy as np
from datetime import datetime

# Load the raw data files
seat_projections_path = "2024 election data/Seat Projections.csv"
pollster_rankings_path = "Final_Pollster_Rankings.csv"
predicted_skew_numbers_path = "Predicted_Skew_Numbers_2023.csv"
initial_values_path = "Initial Data.csv"
seat_projections = pd.read_csv(seat_projections_path)
pollster_rankings = pd.read_csv(pollster_rankings_path)
predicted_skew_numbers = pd.read_csv(predicted_skew_numbers_path)

# Apply the adjustment for skew
seat_projections['NDA'] = seat_projections['NDA'] + 10
seat_projections['I.N.D.I.A.'] = seat_projections['I.N.D.I.A.'] - 6

# Load initial values for WMA calculation from "Initial Data.csv"
initial_data_df = pd.read_csv(initial_values_path)
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
    ranking = pollster_rankings[pollster_rankings['Polling agency'] == agency]['Ranking'].values
    return ranking[0] if len(ranking) > 0 else 0.95
seat_projections['Polling Agency Quality Score'] = [np.mean([calculate_quality_score(agency.strip()) for agency in agencies.split('-')]) for agencies in seat_projections['Polling agency']]

# Calculate Sample Size Score
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
seat_projections.to_csv("WMA_Seat_Projections.csv", index=False)

# Show the first few rows
print(seat_projections.head())