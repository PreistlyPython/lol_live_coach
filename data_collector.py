import pandas as pd
import time
from api_client import RiotAPIClient

class DataCollector:
    def __init__(self, api_client):
        """Initialize the data collector with an API client."""
        self.api_client = api_client
        self.match_data = pd.DataFrame()
        self.champion_winrate_data = pd.DataFrame()
    
    def collect_match_data(self, puuids, num_matches=100):
        matches = []
        for puuid in puuids:
            print(f"Collecting match data for PUUID {puuid}...")
            match_ids = self.api_client.get_match_ids_for_puuids([puuid], num_matches)
            print(f"Number of match IDs fetched for PUUID {puuid}: {len(match_ids[puuid])}")
            
            for match_id in match_ids[puuid]:
                try:
                    match_info = self.api_client.get_match_details(match_id)
                    # Log the raw API response for troubleshooting
                    print(f"Raw API response for match ID {match_id}: {match_info}")
                    if match_info:
                        matches.append(match_info)
                        print(f"Fetched match data for match ID {match_id}")
                    else:
                        print(f"Match ID {match_id} data is missing important keys.")
                except Exception as e:
                    print(f"An error occurred while fetching match data for match ID {match_id}: {e}")
                    continue

        self.match_data = pd.DataFrame(matches)
        print("Match data collection complete.")
        # Log the structure of the final DataFrame
        print(f"Final DataFrame structure: {self.match_data.head()}")
        if self.match_data.empty:
            print("No match data to process.")

    def filter_matches_by_time(self, start_date, end_date):
        """Filter matches based on a time range."""
        if self.match_data.empty:
            print("No match data available to filter.")
            return

        # Ensure start_date and end_date are datetime objects
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter matches based on the game creation timestamp
        self.match_data = self.match_data[
            (self.match_data['gameCreation'] >= start_date) & 
            (self.match_data['gameCreation'] <= end_date)
        ]
        print(f"Filtered matches between {start_date} and {end_date}.")

    def collect_champion_winrate_data(self):
        """Collect champion winrate data."""
        print("Collecting champion win rate data...")
        try:
            champion_stats = self.api_client.get_champion_statistics()
            self.champion_winrate_data = pd.DataFrame(champion_stats)
            print("Champion win rate data collection complete.")
        except Exception as e:
            print(f"An error occurred while collecting champion win rate data: {e}")

    def collect_champion_winrate_data(self, conditions=None):
        """
        Collect win rate data for champions based on specified conditions.
        
        :param conditions: Dict with conditions for data collection (e.g., division, region)
        """
        print("Collecting champion win rate data...")
        try:
            champion_stats = self.api_client.get_champion_statistics(conditions)
            self.champion_winrate_data = pd.DataFrame(champion_stats)
            print(f"Champion win rate data collection complete for conditions: {conditions}")
        except Exception as e:
            print(f"An error occurred while collecting champion win rate data: {e}")

    def process_match_data(self, match_data):
        """Process raw match data to update champion win/loss counts."""
        for match in match_data:
            # Assuming 'match' is a dictionary with match details
            # You will need to adjust the keys based on the actual structure of the match data
            for participant in match['participants']:
                champion_id = participant['championId']
                win = participant['stats']['win']
                
                # Initialize the champion entry in the DataFrame if it doesn't exist
                if champion_id not in self.champion_winrate_data.index:
                    self.champion_winrate_data.loc[champion_id] = {'wins': 0, 'losses': 0}
                
                # Increment win/loss count
                if win:
                    self.champion_winrate_data.loc[champion_id, 'wins'] += 1
                else:
                    self.champion_winrate_data.loc[champion_id, 'losses'] += 1

        # Calculate win rates
        self.champion_winrate_data['winrate'] = self.champion_winrate_data['wins'] / (self.champion_winrate_data['wins'] + self.champion_winrate_data['losses'])
    
    def save_match_data_to_csv(self, file_path):
        """Save match data to a CSV file."""
        if not self.match_data.empty:
            self.match_data.to_csv(file_path, index=False)
            print(f"Match data saved to {file_path}.")
        else:
            print("No match data to save.")

    def save_champion_winrate_data_to_csv(self, file_path):
        """Save champion winrate data to a CSV file."""
        if not self.champion_winrate_data.empty:
            self.champion_winrate_data.to_csv(file_path, index=False)
            print(f"Champion winrate data saved to {file_path}.")
        else:
            print("No champion winrate data to save.")

    def get_match_data(self):
        """Get the collected match data."""
        return self.match_data

    def get_champion_winrate_data(self):
        """Get the collected champion winrate data."""
        return self.champion_winrate_data