import os
import pandas as pd
from data_loading_and_cleaning import load_csv_data

def process_state_data():
    csv_file_path = "data/script_outputs/combined_states_data.csv"
    if not os.path.exists(csv_file_path):
        print(f"Error: Processed state data file does not exist at {csv_file_path}.")
        return

    state_data = load_csv_data(csv_file_path)
    state_data['Date published'] = pd.to_datetime(state_data['Date published'], errors='coerce')
    state_data['Days Difference'] = state_data.groupby('States')['Date published'].transform(lambda x: (x.max() - x).dt.days)

    party_columns = [col for col in state_data.columns if col not in ['States', 'Polling agency', 'Date published', 'Days Difference']]
    state_data[party_columns] = state_data[party_columns].apply(pd.to_numeric, errors='coerce')

    party_scores = state_data[['States']].copy()
    for party in party_columns:
        party_scores[party] = state_data[party] * state_data['Days Difference']

    party_scores = party_scores.groupby('States').sum()
    party_scores['Leading Party'] = party_scores[party_columns].idxmax(axis=1)
    result = party_scores.reset_index()

    output_file = 'data/script_outputs/leading_party_by_state.csv'
    directory = os.path.dirname(output_file)
    if directory and not os.path.exists(directory): os.makedirs(directory)
    result.to_csv(output_file, index=False)
    
    # At the end of process_state_data function:
    print(f"State Results Generated, Saved to {output_file}")