import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class DataAnalysis:
    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)
        
    def analyze_win_rates(self):
        # Calculate win rates
        win_rate_data = self.data.groupby('championName').agg(
            total_games=('championName', 'size'),
            total_wins=('win', 'sum')
        ).reset_index()
        
        win_rate_data['win_rate'] = (win_rate_data['total_wins'] / win_rate_data['total_games']) * 100
        
        # Sort the data for better visualization
        win_rate_data = win_rate_data.sort_values(by='win_rate', ascending=False)

        # Plotting
        plt.figure(figsize=(15, 8))
        sns.barplot(data=win_rate_data, x='championName', y='win_rate')
        plt.xticks(rotation=90)
        plt.title('Champion Win Rates')
        plt.xlabel('Champion Name')
        plt.ylabel('Win Rate (%)')
        plt.show()
        
        # Return the processed data for further analysis if needed
        return win_rate_data

    def analyze_composition(self):
        # Extract team compositions
        team_compositions = self.data.groupby('matchId')['championName'].apply(list)

        # Count the occurrences of each unique team composition
        composition_counts = Counter(map(tuple, team_compositions))
        
        # Calculate win rates
        composition_win_data = {}
        for match_id, champions in team_compositions.items():
            key = tuple(sorted(champions))
            if key not in composition_win_data:
                composition_win_data[key] = {'wins': 0, 'total': 0}
            
            # Assuming 'win' column has boolean values indicating if the team won
            if self.data.loc[self.data['matchId'] == match_id, 'win'].any():
                composition_win_data[key]['wins'] += 1
            composition_win_data[key]['total'] += 1

        # Calculate win rates
        for key in composition_win_data:
            wins = composition_win_data[key]['wins']
            total = composition_win_data[key]['total']
            composition_win_data[key]['win_rate'] = (wins / total) * 100

        # Convert to DataFrame for easier manipulation
        composition_df = pd.DataFrame.from_dict(composition_win_data, orient='index')
        composition_df['composition'] = composition_df.index
        composition_df = composition_df.sort_values(by='win_rate', ascending=False)

        # Visualize the top N compositions
        top_n = 10
        top_compositions = composition_df.head(top_n)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top_compositions, x='composition', y='win_rate')
        plt.xticks(rotation=90)
        plt.title(f'Top {top_n} Team Compositions by Win Rate')
        plt.xlabel('Team Composition')
        plt.ylabel('Win Rate (%)')
        plt.show()

        return top_compositions
    
    def analyze_composition(self):
        # Understand how team compositions affect match outcomes
        pass
    
    def analyze_items(self):
        # Analyze the impact of item choices on win rates
        pass
    
    def additional_analysis(self):
        # Conduct additional analysis based on other relevant data points
        pass
    
    def run_all_analyses(self):
        self.analyze_win_rates()
        self.analyze_composition()
        self.analyze_items()
        self.additional_analysis()