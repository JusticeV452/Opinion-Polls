
import pandas as pd

def convert_polls_moving_averages(input_csv_path, output_xlsx_path):
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
    
    # Save the DataFrame as an Excel (.xlsx) file
    new_df.to_excel(output_xlsx_path, index=False)

# Example usage
if __name__ == "__main__":
    input_csv_path = "Algorithm Output/Polls Moving Averages.csv"
    output_xlsx_path = "Algorithm Output/Converted_Polls_Moving_Averages.xlsx"
    convert_polls_moving_averages(input_csv_path, output_xlsx_path)
