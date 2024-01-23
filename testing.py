from dotenv import load_dotenv
import os
import unittest
import requests_mock
from api_client import RiotAPIClient  # Adjust this import based on your file structure

class TestRiotAPIClient(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv('RIOT_API_KEY')
        self.client = RiotAPIClient(api_key=self.api_key)

    @requests_mock.Mocker()
    def test_get_league_entries(self, m):
        # Mock the API response
        m.get(requests_mock.ANY, json=[{'summonerId': 'test_summoner_id'}])

        # Call the method
        result = self.client.get_league_entries(queue='RANKED_SOLO_5x5', tier='GOLD', division='I')
        
        # Assert the response is as expected
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['summonerId'], 'test_summoner_id')

    @requests_mock.Mocker()
    def test_get_summoner_puuid(self, m):
        """
        Test the get_summoner_puuid method.
        
        Args:
            m (requests_mock.Mocker): The mock object to mock HTTP requests.
        """
        # Step 1: Set up mock data
        summoner_name = "test_summoner"
        expected_puuid = "test_puuid"
        mock_response = {
            "id": "summoner_id",
            "accountId": "account_id",
            "puuid": expected_puuid,
            "name": summoner_name,
            "profileIconId": 1234,
            "revisionDate": 1618365239000,
            "summonerLevel": 30
        }
        
        # Step 2: Set up the mock request
        m.get(f'https://NA1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}', json=mock_response)

        # Step 3: Create an instance of your API client and call get_summoner_puuid
        api_client = RiotAPIClient(self.api_key)
        result_puuid = api_client.get_summoner_puuid(summoner_name)

        # Step 4: Assertions
        self.assertEqual(result_puuid, expected_puuid, "The PUUID returned should match the expected PUUID")

    @requests_mock.Mocker()
    def test_get_matches_from_division(self, m):
        """
        Test the get_matches_from_division method.
        
        Args:
            m (requests_mock.Mocker): The mock object to mock HTTP requests.
        """
        # Mock the API response for get_league_entries
        m.get(requests_mock.ANY, json=[{'summonerId': 'summoner1'}, {'summonerId': 'summoner2'}])

        # Mock the API response for get_match_ids for each summoner
        m.get(requests_mock.ANY, json=['match1', 'match2', 'match3'])

        # Call the method
        result = self.client.get_matches_from_division(queue='RANKED_SOLO_5x5', tier='GOLD', division='I', num_matches_per_summoner=3, num_summoners=2)

        # Assert the response is as expected
        self.assertEqual(len(result), 6)  # Expecting 3 matches per summoner, 2 summoners total
        self.assertIn('match1', result)
        self.assertIn('match2', result)
        self.assertIn('match3', result)

    @requests_mock.Mocker()
    def test_get_matches_from_division(self, m):
        # Mock the league entries with summoner names
        mock_league_entries = [
            {'summonerId': 'summoner1', 'summonerName': 'SummonerOne'}, 
            {'summonerId': 'summoner2', 'summonerName': 'SummonerTwo'}
        ]
        m.get('https://na1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/I', json=mock_league_entries)

        # Mock the summoner details endpoint for each summoner
        for summoner in mock_league_entries:
            summoner_name = summoner['summonerName']
            mock_puuid = f"test_puuid_{summoner_name}"
            m.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}', json={'puuid': mock_puuid})

        # Mock the match endpoint for each PUUID
        mock_match_ids = ['match1', 'match2', 'match3']
        for summoner in mock_league_entries:
            mock_puuid = f"test_puuid_{summoner['summonerName']}"
            m.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{mock_puuid}/ids', json=mock_match_ids)

        # Fetch PUUIDs from mocked summoner details
        puuids = [self.client.get_summoner_puuid(summoner['summonerName']) for summoner in mock_league_entries]
        
        # Call the method with PUUIDs
        result = self.client.get_matches_from_division(puuids, num_matches_per_summoner=3)

        # Assert the response is as expected
        self.assertEqual(len(result), 6)  # Expecting 3 matches per summoner, 2 summoners total
        self.assertIn('match1', result)
        self.assertIn('match2', result)
        self.assertIn('match3', result)

    @requests_mock.Mocker()
    def test_get_match_ids(self, m):
        # Initialize the RiotAPIClient
        api_client = RiotAPIClient(self.api_key)

        # Mock the match endpoint
        summoner_name = 'SummonerOne'
        mock_puuid = 'test_puuid'
        m.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}', json={'puuid': mock_puuid})
        m.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{mock_puuid}/ids', json=['match1', 'match2', 'match3'])

        # Call the method
        result = api_client.get_match_ids(mock_puuid, num_matches=3)

        # Assert the response is as expected
        self.assertEqual(len(result), 3)
        self.assertIn('match1', result)
        self.assertIn('match2', result)
        self.assertIn('match3', result)

    @requests_mock.Mocker()
    def test_get_champion_mastery(self, m):
        # Mock the API response
        m.get(requests_mock.ANY, json={'championId': 123, 'championLevel': 5})
        
        # Call the method
        result = self.client.get_champion_mastery(summoner_id='test_summoner_id')

        # Assert the response is as expected
        self.assertEqual(result['championId'], 123)
        self.assertEqual(result['championLevel'], 5)

    # Add similar tests for filter_matches_by_division, get_matches_from_division, get_match_ids
    # Remember to mock the responses and assert that the result is as expected

    # Since filter_matches_by_division and get_matches_from_division depend on the API responses from other methods,
    # you may need to mock those responses within these tests as well.

    # For get_match_ids, you'll need to mock the pagination behavior, so this might involve setting up multiple mocked responses
    # to simulate retrieving multiple pages of data.

if __name__ == '__main__':
    unittest.main()