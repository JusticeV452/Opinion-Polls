import pandas as pd
import numpy as np

POLLSTERS_RANKING_DF_PATH = 'data/constant_initial_data/Final_Pollster_Rankings.csv'
pollsters_ranking_df = pd.read_csv(POLLSTERS_RANKING_DF_PATH)

def calculate_scores(seat_projections):
    """
    Calculates various scores for each poll in the seat projections DataFrame.

    The function calculates the following scores:
    - Polling Agency Quality Score: The average ranking of the polling agencies that conducted the poll.
    - Sample Size Score: A score based on the sample size of the poll, with larger sample sizes receiving higher scores.
    - Margin of Error Score: A score based on the margin of error of the poll, with smaller margins of error receiving higher scores.
    - Recency Score: A score based on how recent the poll was conducted, with more recent polls receiving higher scores.
    - Overall Poll Quality: A weighted average of the above scores.

    Returns:
    DataFrame: The input DataFrame with the following additional columns:
        - 'Polling Agency Quality Score'
        - 'Sample Size Score'
        - 'Margin of Error Score'
        - 'Recency Score'
        - 'Overall Poll Quality'
    """
    seat_projections['Polling Agency Quality Score'] = [
        np.mean([
            pollsters_ranking_df[pollsters_ranking_df['Polling agency'] == agency.strip()]['Ranking'].values[0] if len(pollsters_ranking_df[pollsters_ranking_df['Polling agency'] == agency.strip()]['Ranking'].values) > 0 else 0.95
            for agency in agencies.split('-')
        ])
        for agencies in seat_projections['Polling agency']
    ]

    max_sample_size = seat_projections['Sample size'].max()
    min_sample_size = seat_projections['Sample size'].min()
    scaling_factor = (1.5 - 0.5) / (max_sample_size - min_sample_size)
    seat_projections['Sample Size Score'] = seat_projections['Sample size'].apply(lambda x: 0.5 + scaling_factor * (x - min_sample_size))
    
    seat_projections['Margin of Error'] = seat_projections['Margin of Error'].astype(str).str.replace('[^\d]', '', regex=True).astype(float)
    
    median_margin_of_error = seat_projections['Margin of Error'].median()
    seat_projections['Margin of Error Score'] = seat_projections['Margin of Error'].apply(lambda x: 0.5 + 1 * (median_margin_of_error - x) / median_margin_of_error)

    max_days_to_election = seat_projections['Days to Election'].max()
    seat_projections['Recency Score'] = seat_projections['Days to Election'].apply(lambda x: 0.5 + (max_days_to_election - x) / max_days_to_election)

    seat_projections['Overall Poll Quality'] = 0.4 * seat_projections['Recency Score'] + 0.25 * seat_projections['Polling Agency Quality Score'] + 0.3 * seat_projections['Sample Size Score'] + 0.05 * seat_projections['Margin of Error Score']
