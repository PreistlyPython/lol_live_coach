
from api_client import RiotAPIClient
from data_collector import DataCollector
from inference import InferenceEngine
from config import RIOT_API_KEY


def main():
    # Initialize the Riot API client with your API key
    api_client = RiotAPIClient(RIOT_API_KEY)
    data_collector = DataCollector(api_client)

    # Define the parameters for the division and number of matches
    num_matches_per_puuid = 10  # Number of matches to fetch per PUUID
    division = 'I'
    tier = 'BRONZE'
    queue = 'RANKED_SOLO_5x5'
    num_summoners = 10  # Number of summoners to fetch PUUIDs for

    # Fetch league entries to get summoner names
    league_entries = api_client.get_league_entries(queue, tier, division, page=1)

    # Fetch PUUIDs for the summoner names
    puuids = [api_client.get_summoner_puuid(entry['summonerName']) for entry in league_entries[:num_summoners]]

    # Fetch and store match details for the PUUIDs
    data_collector.collect_match_data(puuids, num_matches_per_puuid)

    # Save match data to a CSV file
    data_collector.match_data.to_csv('match_data.csv', index=False)
    print("Match data saved to match_data.csv.")

if __name__ == '__main__':
    main()