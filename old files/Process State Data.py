import pandas as pd
import subprocess
import os

# Full path to tableau-prep-cli
tableau_prep_cli_path = '/Applications/Tableau Prep Builder 2023.2.app/Contents/scripts/tableau-prep-cli'
# Run the Tableau Flow and wait for it to complete
flow_file_path = '/Users/dwaipayanbanerjee/Dropbox (Personal)/Coding Workshop/Opinion Polls/python scripts/scrape wikipedia/State_Cleaning_Flow.tfl'  # Adjust this path as needed

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


# Read the raw data with the file location
file_location = '2024 election data/Combined States Data.csv'
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
output_file = 'leading_party_by_state.csv'
result.to_csv(output_file, index=False)

print(f"Result saved to '{output_file}'")
