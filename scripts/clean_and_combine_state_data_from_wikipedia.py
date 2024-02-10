import pandas as pd
import os

def clean_and_combine_state_data():
    # Load the CSV files
    directory = 'data/wikipedia_scrape/'
    csv_files = [f for f in os.listdir(directory) if f.endswith(').csv')]
    dfs = []

    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        df['File Paths'] = file  # Add the file path as a column
        dfs.append(df)

    # Combine all dataframes into a single dataframe
    combined_df = pd.concat(dfs, ignore_index=True)

    # Cleaning steps:
    # 1. Change 'Date published' to datetime type
    combined_df['Date published'] = pd.to_datetime(combined_df['Date published'], errors='coerce')

    # 2. Extract and trim state names from 'File Paths'
    combined_df['States'] = combined_df['File Paths'].str.extract(r'^(.*?) \(').fillna('').apply(lambda x: x.str.strip())
    cols = combined_df.columns.tolist()
    cols.insert(2, cols.pop(cols.index('States')))
    combined_df = combined_df[cols]

    # Convert 'Lead' column values to uppercase
    combined_df['Lead'] = combined_df['Lead'].str.upper()

    # Replace "I.N.D.I.A" with "I.N.D.I.A."
    combined_df['Lead'] = combined_df['Lead'].replace({"I.N.D.I.A": "I.N.D.I.A."})

    # 3. Now remove 'Margin of Error' and 'Lead' fields
    combined_df.drop(['File Paths', ], axis=1, inplace=True)

    #Drop rows with missing values
    columns_to_check = ['NDA', 'I.N.D.I.A.', 'Others']
    combined_df = combined_df[combined_df[columns_to_check].notna().any(axis=1)]

    # Standardize the 'Date published' column format to YYYY-MM-DD
    combined_df['Date published'] = combined_df['Date published'].dt.strftime('%Y-%m-%d')

    # Save the cleaned dataframe
    cleaned_csv_path = 'data/script_outputs/combined_states_data.csv'
    combined_df.to_csv(cleaned_csv_path, index=False)
