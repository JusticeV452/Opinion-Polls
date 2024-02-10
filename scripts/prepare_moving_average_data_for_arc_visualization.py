import pandas as pd

def convert_polls_moving_averages(input_csv_path, output_csv_path):

    # Read the input CSV file
    polls_moving_averages_df = pd.read_csv(input_csv_path)
    
    # Extract the last row and relevant columns
    last_row = polls_moving_averages_df.iloc[-1][['NDA_Moving_Average', 'INDIA_Moving_Average', 'Others_Moving_Average']]
    
    # Create an empty DataFrame to store the new data
    new_df = pd.DataFrame(columns=['Seat #', 'Party'])
    
    # Calculate the number of rows for each category based on the last row data
    nda_rows = int(last_row['NDA_Moving_Average'])
    india_rows = int(last_row['INDIA_Moving_Average'])
    others_rows = int(last_row['Others_Moving_Average'])
    
    # Populate the DataFrame
    new_df['Seat #'] = list(range(1, nda_rows + others_rows + india_rows + 1))
    new_df['Party'] = ['Others'] * others_rows + ['I.N.D.I.A.'] * india_rows + ['NDA'] * nda_rows
    
    # Save the DataFrame as a CSV file
    new_df.to_csv(output_csv_path, index=False)

def prepare_moving_average_data():
    # Convert the polls moving averages data to a format that can be used for the arc visualization
    input_csv_path = "data/script_outputs/polls_moving_averages.csv"
    output_csv_path = "data/script_outputs/converted_polls_moving_averages.csv"
    convert_polls_moving_averages(input_csv_path, output_csv_path)