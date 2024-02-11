
# Opinion-Polls Project: 2024 Indian General Elections

## Introduction
The Opinion-Polls project is dedicated to aggregating, cleaning, and analyzing opinion poll data for the 2024 Indian General Elections from various reputable Indian polling and news agencies. This initiative aims to create a comprehensive polls of polls, providing a snapshot of current public opinion and projections for the upcoming elections.

## Features
- **Data Aggregation**: Gathers opinion poll data from reputable Indian polling and news agencies, ensuring a broad and diverse dataset that reflects public opinion accurately.
- **Data Cleaning and Analysis**: Employs a detailed methodology, as outlined in our codebook, for data cleaning and analysis to ensure the accuracy and reliability of the aggregated polls.
- **Visualization**: Provides basic Tableau visualizations that map current projections, offering an intuitive understanding of the election landscape.

## Project Structure
- `/data`: Contains the raw and processed data files, including initial datasets, script outputs, and data scraped from reputable sources.
  - `/constant_initial_data`: Stores initial datasets used across analyses.
  - `/script_outputs`: Contains processed data ready for analysis and visualization.
  - `/wikipedia_scrape`: Holds supplementary data scraped for analysis.
- `/scripts`: Comprises Python scripts for data processing and analysis, reflecting the methodology detailed in the codebook.
  - `calculate_poll_quality.py`: Assesses the quality of each poll based on predefined criteria.
  - `combine_state_data_from_wikipedia.py`: Merges state-wise data for a comprehensive dataset.
  - `data_loading_and_cleaning.py`: Manages the initial loading and cleaning of raw poll data.
  - `generate_seat_projections.py`: Projects seat allocations based on aggregated poll data.
  - `main.py`: The main script orchestrating the execution of various components of the project.
  - `prepare_moving_average_for_visualization.py`: Prepares data for visualization by calculating moving averages.
  - `process_state_data.py`: Processes state-wise data for in-depth analysis.
  - `wikipedia_scraping_processing.py`: Scrapes and processes supplementary data for analysis.
- `/tableau`: Contains Tableau workbooks for data visualization, offering insights into current election projections.

## Getting Started
1. **Clone the Repository**: Clone this repository to your local machine to get started.
2. **Install Dependencies**: Make sure Python is installed, and install the required Python packages as listed in `requirements.txt`.
3. **Explore the Codebook**: Review the methodology and data processing steps detailed in the codebook located in `/documentation/codebook.md`.
4. **Run the Analysis**: Execute the data loading, cleaning, and analysis scripts as per the instructions in the codebook.
5. **Visualize the Data**: Open the provided Tableau workbooks to explore the visualizations of current election projections.

## Contributing
This project is in its early development phase and welcomes contributions from the community. Whether it's enhancing data sources, refining analysis scripts, improving visualizations, or expanding documentation, your input can significantly impact this project's growth and accuracy. Please refer to `CONTRIBUTING.md` for more details on how to contribute.

## License
This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for more information.

## Acknowledgments
- Data sources: Reputed Indian polling and news agencies.
- Contributors: [List the main contributors here]
