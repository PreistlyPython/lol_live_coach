import requests
import time
from config import RIOT_API_KEY
from riotwatcher import LolWatcher, ApiError

class RiotAPIClient:
    def __init__(self, api_key, region='NA1'):
        self.api_key = api_key
        self.region = region
        self.base_url = f'https://{self.region}.api.riotgames.com/lol/'  # Base URL
        self.lol_watcher = LolWatcher(self.api_key)

    def _request(self, endpoint, params={}):
        headers = {'X-Riot-Token': self.api_key}
        full_url = self.base_url + endpoint.lstrip('/')
        response = requests.get(full_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_league_entries(self, queue, tier, division, page=1):
        endpoint = f'league/v4/entries/{queue}/{tier}/{division}'
        params = {'page': page}
        return self._request(endpoint, params)
    
    def get_champion_mastery(self, summoner_id):
        """Get champion mastery for a given summoner."""
        endpoint = f'champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}'
        return self._request(endpoint)
    
    def filter_matches_by_division(self, tier='DIAMOND', division='I'):
        """Filter collected match data to include only matches played by summoners in the specified division."""
        if self.match_data.empty:
            print("No match data available to filter.")
            return

        # Fetch league data for summoners in the specified division
        summoners_in_division = set()
        league_entries = self.api_client.get_league_entries(tier=tier, division=division)
        for entry in league_entries:
            summoner_id = entry['summonerId']
            summoners_in_division.add(summoner_id)

        # Filter matches
        self.match_data = self.match_data[self.match_data['summonerId'].isin(summoners_in_division)]
        print(f"Filtered matches to include only those played by summoners in {tier} {division}.")
    
    def get_match_ids_for_puuids(self, puuids, num_matches_per_puuid=20):
        """
        Fetch match IDs for a list of PUUIDs.

        :param puuids: A list of PUUIDs.
        :param num_matches_per_puuid: Number of matches to fetch per PUUID.
        :return: A dictionary where keys are PUUIDs and values are lists of match IDs.
        """
        match_ids_per_puuid = {}
        for puuid in puuids:
            try:
                # Fetch match IDs for the PUUID
                match_ids = self.lol_watcher.match.matchlist_by_puuid(self.region, puuid, count=num_matches_per_puuid)
                match_ids_per_puuid[puuid] = match_ids
                print(f"Match IDs fetched for PUUID {puuid}: {len(match_ids)} matches.")
            except ApiError as err:
                print(f"An error occurred while fetching match IDs for PUUID: {puuid}: {err}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        return match_ids_per_puuid
    
    def get_champion_statistics(self):
        """
        Fetch statistics for champions.

        :return: Champion statistics.
        """
        try:
            # Modify the endpoint and parameters according to the Riot API documentation and your needs
            champion_stats = self._request('endpoint/for/champion/statistics')
            return champion_stats
        except ApiError as err:
            print(f"An error occurred while fetching champion statistics: {err}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    def get_matches_from_division(self, puuids, num_matches_per_summoner):
        match_ids = []
        for puuid in puuids:
            summoner_match_ids = self.get_match_ids(puuid, num_matches_per_summoner)  # Call with PUUID
            match_ids.extend(summoner_match_ids)
        return match_ids
    
    def extract_summoner_names_from_matches(match_data):
        """
        Extract summoner names from match data.

        :param match_data: The match data from which to extract summoner names.
        :return: A list of summoner names.
        """
        summoner_names = []
        for match in match_data:
            participant_identities = match.get('participantIdentities', [])
            for participant_identity in participant_identities:
                player = participant_identity.get('player', {})
                summoner_name = player.get('summonerName')
                if summoner_name:
                    summoner_names.append(summoner_name)
        return summoner_names

    def get_top_players(self, region, queue, tier, division, page=1):
        """
        Get a list of top players in a specified region, queue, tier, and division.

        :param region: The region where the players are located.
        :param queue: The queue type (e.g., 'RANKED_SOLO_5x5').
        :param tier: The tier (e.g., 'CHALLENGER').
        :param division: The division (e.g., 'I').
        :param page: The page number for pagination.
        :return: A list of top players.
        """
        endpoint = f'league-exp/v4/entries/{queue}/{tier}/{division}'
        params = {'page': page}
        try:
            top_players = self.lol_watcher.league.entries(region, queue, tier, division, page)
            print(f"Retrieved {len(top_players)} top players from {region}.")
            return top_players
        except ApiError as err:
            print(f"An error occurred while fetching top players: {err}")
            return None
        
    
    def get_summoner_puuid(self, summoner_name):
        try:
            summoner_details = self.lol_watcher.summoner.by_name(self.region, summoner_name)
            puuid = summoner_details.get('puuid')
            if puuid:
                print(f"Extracted PUUID: {puuid}")  # Log the extracted PUUID
                return puuid
            else:
                print(f"PUUID not found for summoner: {summoner_name}")
                return None
        except ApiError as err:
            if err.response.status_code == 404:
                print(f"Summoner '{summoner_name}' not found.")
            else:
                print(f"An error occurred: {err}")

    def get_match_details(self, match_id):
        """Fetch detailed information for a match by its ID."""
        try:
            match_details = self.lol_watcher.match.by_id(self.region, match_id)
            return match_details
        except ApiError as err:
            print(f"An error occurred while fetching details for match ID {match_id}: {err}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    def get_match_ids(self, puuid, num_matches=10):
        try:
            # Fetch match IDs using the PUUID
            match_ids = self.lol_watcher.match.matchlist_by_puuid(self.region, puuid, count=num_matches)
            return match_ids
        except ApiError as err:
            # Handle specific API errors (e.g., rate limits, summoner not found, etc.)
            print(f"An error occurred while fetching match IDs for PUUID: {puuid}: {err}")
            return []
        except Exception as e:
            # Handle other potential errors (e.g., network issues)
            print(f"An unexpected error occurred: {e}")
            return []

