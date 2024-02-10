import os
from wikipedia_scraping_processing import get_and_process_tables
from clean_and_combine_state_data_from_wikipedia import clean_and_combine_state_data
from process_state_data import process_state_data
from generate_seat_projections import generate_seat_projections
from prepare_moving_average_data_for_arc_visualization import prepare_moving_average_data

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_heading(message):
    print(f"\033[1;91m{message}\033[0m")

def main():
    clear_terminal()

    print_heading("Starting Scraping Process...")
    get_and_process_tables()
    print_heading('Scraping Finished.')
    
    print_heading("Cleaning and Combining State Data...")
    clean_and_combine_state_data()
    print_heading("State Data Cleaned and Combined.")

    print_heading("Generating Projections...")
    generate_seat_projections()
    print_heading("Projections Generated.")
    
    print_heading("Preparing Data for Arc Visualization...")
    prepare_moving_average_data()
    print_heading("Data Prepared for Arc Visualization.")

    print_heading("Generating State Data...")
    process_state_data()
    print_heading("State Data Generated.")

if __name__ == "__main__":
    main()