"""
PSN Dashboard Generator
Author: Muntakim Rahman
Description: Interacts with PlayStation Network API (via PSNAWP) to Fetch User Data
    (Played Games, Playtime, Trophies) and Generates Visualizations using Altair.
    Data is Saved to CSV for Backup and Dashboard is Exported as JSON, HTML, PNG, SVG.
"""

# Import Packages
import pandas as pd
import altair as alt

import json
import os
from datetime import timedelta
from dotenv import load_dotenv

from typing import Optional

from psnawp_api import PSNAWP
from psnawp_api.models.trophies import PlatformType

PWD = os.path.dirname(os.path.abspath(__file__))

class PSN_API:
    """Handles PSN API Interactions via PSNAWP"""

    def __init__(self, npsso_code: str):
        self.psnawp = PSNAWP(npsso_code)

    def getClient(self):
        """Get Authenticated Client (Your Account)"""
        return self.psnawp.me()

    def getUser(self, username: str):
        """Get User by Online ID"""
        try:
            return self.psnawp.user(username = username)
        except Exception as e:
            print(f"Failed to Get User {username}: {e}")
            return None

    def getTitleStats(self, user) -> pd.DataFrame:
        """Fetch User's Played Games with Playtime Data (PS4/PS5 Only)"""
        try:
            titles = []
            for title in user.title_stats():
                play_hours = title.play_duration.total_seconds() / 3600.0 if title.play_duration else 0.0 # Convert TimeDelta to Hours

                titles.append({
                    'title_id': title.title_id, # Unique Identifier for the Game
                    'name': title.name, # Game Title
                    'category': str(title.category).split('.')[-1] if title.category else 'UNKNOWN', # Platform (PS4/PS5)
                    'playtime_forever': round(play_hours, 2), # Total Playtime in Hours
                })

            if titles:
                print(pd.DataFrame(titles))
                return pd.DataFrame(titles)
            else:
                print("No Title Stats Found")
                return pd.DataFrame()
        except Exception as e:
            print(f"Failed to Get Title Stats: {e}")
            return pd.DataFrame()

    def getTrophySummary(self, user) -> dict:
        """Fetch User's Trophy Summary"""
        try:
            summary = user.trophy_summary()
            return {
                'level': summary.trophy_level,
                'platinum': summary.earned_trophies.platinum,
                'gold': summary.earned_trophies.gold,
                'silver': summary.earned_trophies.silver,
                'bronze': summary.earned_trophies.bronze,
            }
        except Exception as e:
            print(f"Failed to Get Trophy Summary: {e}")
            return {'level': 0, 'platinum': 0, 'gold': 0, 'silver': 0, 'bronze': 0}

class PSN_User:
    """Represents a PSN User and Their Gaming Data"""

    CUSTOM_NAMES = {
        "Harvest Moon\u00ae: A Wonderful Life Special Edition": "Harvest Moon: AWL",
        "BATMAN\u2122: ARKHAM KNIGHT": "Batman: Arkham Knight",
        "God of War Ragnar\u00f6k": "God of War Ragnarok",
        "Marvel's Spider-Man: Miles Morales": "Spider-Man: Miles Morales",
        "Marvel's Spider-Man": "Spider-Man",
        "inFAMOUS\u2122 Second Son": "inFAMOUS Second Son",
    }

    HIDDEN_APPS = {
        "YouTube",
        "Netflix",
        "Spotify"
    }

    def __init__(self, username: str, api_client: PSN_API, use_client: bool = False):
        self.username = username
        self.api_client = api_client

        self.trophy_level = 0
        self.trophy_counts = {}

        # PSN Data
        self.stats_df = pd.DataFrame()

        self._getData(use_client)

    def _renameGames(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Custom Game Name Mappings to DataFrame"""
        if df.empty or ('name' not in df.columns):
            return df

        mapped_df = df.copy()

        # Apply Mappings
        for psn_name, custom_name in self.CUSTOM_NAMES.items():
            mapped_df.loc[mapped_df['name'] == psn_name, 'name'] = custom_name
        return mapped_df

    def getCurrentGameNames(self) -> list:
        """Get Current Game Names for Mapping Reference"""
        if self.stats_df.empty:
            return []
        return sorted(self.stats_df['name'].unique().tolist())

    def _getData(self, use_client: bool = False) -> None:
        """Get All User Data from PSN API"""
        try:
            if use_client:
                user = self.api_client.getClient()
                self.username = user.username
            else:
                user = self.api_client.getUser(self.username)

            if not user:
                raise ValueError(f"Could Not Find PSN User: {self.username}")

            # Get Title Stats (Playtime)
            self.stats_df = self.api_client.getTitleStats(user)

            # Get Trophy Summary
            self.trophy_counts = self.api_client.getTrophySummary(user)
            self.trophy_level = self.trophy_counts.get('level', 0)

            self._compileStats()

            print(f"Successfully Fetched Data for {self.username}")
            print(f"Games Played: {len(self.stats_df)}")
            print(f"Trophy Level: {self.trophy_level}")

        except Exception as e:
            print(f"Error Fetching User Data: {e}")
            self._loadFromCSV()

    def _loadFromCSV(self) -> None:
        """Load Data from Backup CSV if API Fails"""
        csv_file = f"{self.username}_PSNData.csv"
        if os.path.exists(os.path.join(PWD, csv_file)):
            print(f"Loading Data from CSV File: {csv_file}")
            self.stats_df = pd.read_csv(os.path.join(PWD, csv_file))
            if not self.stats_df.empty:
                row = self.stats_df.iloc[0]
                if 'trophy_level' in self.stats_df.columns:
                    self.trophy_level = row['trophy_level']
                for key in ['platinum', 'gold', 'silver', 'bronze']:
                    col = f'trophy_{key}'
                    if col in self.stats_df.columns:
                        self.trophy_counts[key] = int(row[col])
        else:
            print("No Backup Data Available")

    def _compileStats(self) -> None:
        """Compile and Clean Stats"""
        if self.stats_df.empty:
            print("No Game Data Available")
            return

        stats_df = self.stats_df.copy()
        stats_df = stats_df[~stats_df['name'].isin(self.HIDDEN_APPS)]
        stats_df['trophy_level'] = self.trophy_level
        for key in ['platinum', 'gold', 'silver', 'bronze']:
            stats_df[f'trophy_{key}'] = self.trophy_counts.get(key, 0)
        stats_df = stats_df.fillna(0).sort_values('playtime_forever', ascending = False)
        self.stats_df = self._renameGames(stats_df)

        self.saveData()

    def saveData(self, filename: Optional[str] = None) -> None:
        """Save User Data to CSV"""
        if filename is None:
            filename = f"{self.username}_PSNData.csv"

        if not self.stats_df.empty:
            self.stats_df.to_csv(os.path.join(PWD, filename), index = False)
            print(f"Data Saved to {filename}")

    def getTopData(self, n: int = 15) -> pd.DataFrame:
        """Get Top N Games By Playtime"""
        return self.stats_df.nlargest(n, 'playtime_forever')[
            ['name', 'playtime_forever', 'title_id']
        ].sort_values('playtime_forever', ascending = False)

    def getNumberPlayed(self) -> int:
        """Get Number of Games with Playtime > 0"""
        return (self.stats_df['playtime_forever'] > 0).sum()

    def getTotalPlaytime(self) -> float:
        """Get Total Playtime Across Games"""
        return self.stats_df['playtime_forever'].sum()

class PSN_Dashboard:
    """Creates Visualizations for PSN User Data"""

    def __init__(self, user: PSN_User):
        self.user = user
        self.colors = [
            "#00008B", "#32CD32", "#00CED1", "#A8D7E7",
            "#808080", "#FF4500", "#0000FF", "#3D3A38",
            "#800080", "#FFA500","#006400", "#8B0000",
            "#FFD700", "#4682B4", "#2E8B57"
        ]

        self.dashboard = None
        self.generateDashboard()

    def generatePlaytimeChart(self, top_n: int = 10) -> alt.Chart:
        """Generate Pie Chart of Top Games by Playtime"""
        top_df = self.user.getTopData(top_n).copy()
        total_playtime = top_df['playtime_forever'].sum()
        top_df['playtime_percentage'] = (top_df['playtime_forever'] / total_playtime * 100).round(2)

        return alt.Chart(top_df).mark_arc(
            stroke = 'black', strokeWidth = 1
        ).encode(
            theta = alt.Theta('playtime_percentage:Q'),
            color = alt.Color(
                'name:N',
                scale = alt.Scale(range = self.colors),
                legend = alt.Legend(
                    orient = 'bottom', direction = 'horizontal', columns = 5,
                    padding = 75, rowPadding = 10, columnPadding = 75,
                    title = '', titleAlign = 'center',
                    labelFontSize = 10, titleFontSize = 16,
                ),
                sort = None
            ),
            tooltip = [
                alt.Tooltip('name:N', title = 'Game'),
                alt.Tooltip('playtime_forever:Q', title = 'Time (Hrs)', format = '.1f'),
                alt.Tooltip('playtime_percentage:Q', title = 'Playtime (%)', format = '.2f')
            ]
        ).properties(
            width = 700, height = 400,
            title = alt.TitleParams(
                text = f"Top Games",
                subtitle = f"Total Playtime: {total_playtime:.1f} Hrs",
                anchor = 'middle', fontSize = 20, subtitleFontSize = 16
            )
        )

    def generateLevelDisplay(self) -> alt.Chart:
        """Generate Trophy Level Display"""
        data = pd.DataFrame({
            'Metric': ['Trophy Level'],
            'Value': [self.user.trophy_level]
        })

        return alt.Chart(data).mark_text(
            align = 'center', baseline = 'middle',
            fontSize = 80, fontWeight = 'bold', color = '#141331'
        ).encode(
            x = alt.X('Metric:N', axis = None),
            y = alt.value(50),
            text = 'Value:Q'
        ).properties(
            width = 300, height = 150,
            title = alt.TitleParams(text = 'Trophy Level', anchor = 'middle', fontSize = 20)
        )

    def generatePlayedDisplay(self) -> alt.Chart:
        """Create Played Games Display"""
        data = pd.DataFrame({
            'Metric': ['Played'],
            'Value': [self.user.getNumberPlayed()]
        })

        return alt.Chart(data).mark_text(
            align = 'center', baseline = 'middle',
            fontSize = 80, fontWeight = 'bold', color = '#141331'
        ).encode(
            x = alt.X('Metric:N', axis = None),
            y = alt.value(50),
            text = 'Value:Q'
        ).properties(
            width = 300, height = 150,
            title = alt.TitleParams(text = 'Played', anchor = 'middle', fontSize = 20)
        )

    def generateTrophyChart(self) -> alt.Chart:
        """Generate Horizontal Bar Chart of Trophy Counts"""
        trophy_data = pd.DataFrame([
            {'type': 'Platinum', 'count': self.user.trophy_counts.get('platinum', 0)},
            {'type': 'Gold', 'count': self.user.trophy_counts.get('gold', 0)},
            {'type': 'Silver', 'count': self.user.trophy_counts.get('silver', 0)},
            {'type': 'Bronze', 'count': self.user.trophy_counts.get('bronze', 0)},
        ])

        # Remove Trophy Types with Zero Count
        trophy_data = trophy_data[trophy_data['count'] > 0]

        total = trophy_data['count'].sum()

        return alt.Chart(trophy_data).mark_bar(
            stroke = 'black', strokeWidth = 1
        ).encode(
            x = alt.X('count:Q', axis = alt.Axis(title = '', tickMinStep = 1)),
            y = alt.Y(
                'type:N',
                sort = ['Platinum', 'Gold', 'Silver', 'Bronze'],
                axis = alt.Axis(title = '', labelFontSize = 13)
            ),
            color = alt.Color(
                'type:N',
                scale = alt.Scale(
                    domain = ['Platinum', 'Gold', 'Silver', 'Bronze'],
                    range  = ['#B9F2FF', '#FFD700', '#C0C0C0', '#CD7F32']
                ),
                legend = None
            ),
            tooltip = [
                alt.Tooltip('type:N',  title = 'Trophy'),
                alt.Tooltip('count:Q', title = 'Count'),
            ]
        ).properties(
            width = 250, height = 150,
            title = alt.TitleParams(
                text     = 'Trophies',
                subtitle = f'Total: {total:,}',
                anchor   = 'middle', fontSize = 20, subtitleFontSize = 14
            )
        )

    def generateDashboard(self) -> None:
        """Generate Complete Dashboard"""
        playtime_chart = self.generatePlaytimeChart()
        stats_chart = (
            self.generateLevelDisplay() & self.generatePlayedDisplay() & self.generateTrophyChart()
        ).properties(
            title = alt.TitleParams(text = 'Player Stats', anchor = 'middle', fontSize = 30)
        )

        self.dashboard = (stats_chart | playtime_chart).resolve_scale(color = 'independent').properties(
            padding = {"left": 250, "right": 250, "top": 0, "bottom": 0},
            title = alt.TitleParams(
                text = f"{self.user.username}'s PSN Dashboard",
                anchor = 'middle', fontSize = 40
            ),
        ).configure_view(
            strokeWidth = 1.5,
            strokeOpacity = 0,
        ).configure_axis(
            labelFontSize = 12, titleFontSize = 16
        ).configure_legend(
            labelFontSize = 12, titleFontSize = 16
        )

    def updateTemplate(self, template_json: dict, output_path: str) -> None:
        """Update Existing JSON Template with Fresh Data while Preserving Structure"""
        def _get_keys(current_json: dict) -> dict:
            keys_dict = {
                'Level': None,
                'Played': None,
                'Games': None
            }
            for key, data in current_json['datasets'].items():
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    if (data[0].get('Metric') == 'Trophy Level'):
                        keys_dict['Level'] = key
                    elif (data[0].get('Metric') == 'Played'):
                        keys_dict['Played'] = key
                    elif ('name' in data[0]) and ('playtime_forever' in data[0]):
                        keys_dict['Games'] = key
            return keys_dict

        try:
            # Load Dashboard JSON with Fresh Data
            dashboard_json = self.dashboard.to_dict()
            dashboard_datasets = dashboard_json.get('datasets', {})

            # Identify Keys for Level, Played, Games Data in Template
            template_keys = _get_keys(template_json)
            dashboard_keys = _get_keys(dashboard_json)

            # Identify Data Keys in Dashboard JSON
            if (not dashboard_keys['Level']):
                print("ERROR: Could Not Identify Level Key in Template")
            if (not dashboard_keys['Played']):
                print("ERROR: Could Not Identify Played Key in Template")
            if (not dashboard_keys['Games']):
                print("ERROR: Could Not Identify Games Key in Template")

            for key in template_keys.keys():
                updated_key = dashboard_keys[key]
                if key and updated_key:
                    template_json['datasets'][template_keys[key]] = dashboard_datasets[updated_key]
                else:
                    print(f"Warning: Missing Data for Key '{key}' - Skipping Update for this Dataset")

            # Save Updated JSON
            with open(output_path, 'w') as f:
                json.dump(template_json, f, indent = 2)

            print(f"Template Updated Successfully: {output_path}")
        except Exception as e:
            print(f"Error Updating Template: {e}")

    def save(self, filename: Optional[str] = None) -> None:
        """Save Dashboard to File"""
        if self.dashboard is None:
            print("Dashboard Not Generated")
            return

        if filename is None:
            filename = f"{self.user.username}_Dashboard"

        if not os.path.exists(os.path.join(PWD, 'Charts')):
            os.makedirs(os.path.join(PWD, 'Charts'))

        with open(os.path.join(PWD, f"Charts/{filename}.json"), 'w') as f:
            json.dump(self.dashboard.to_dict(), f, indent = 2)

        # Load Dashboard from JSON File
        with open(os.path.join(PWD, f"Charts/{filename}.json"), 'r') as f:
            spec = json.load(f)

        self.dashboard = alt.Chart.from_dict(spec)

        # Save as HTML (Interactive)
        with open(os.path.join(PWD, f"Charts/{filename}.html"), 'w') as f:
            f.write(self.dashboard.to_html())

        self.dashboard.save(os.path.join(PWD, f"Charts/{filename}.png")) # Save as PNG (Static)
        self.dashboard.save(os.path.join(PWD, f"Charts/{filename}.svg")) # Save as SVG (Vector)

        # Replace All JSON with Fresh Data while Preserving Structure
        for file in os.listdir(os.path.join(PWD, 'Charts')):
            if file.endswith('.json'):
                template_path = os.path.join(PWD, 'Charts', file)

                with open(template_path, 'r') as f:
                    template_json = json.load(f)

                self.updateTemplate(template_json, template_path)

if __name__ == '__main__':
    load_dotenv()

    USERNAME = 'Dipto_9999'
    USE_CLIENT = True # True = Use Authenticated Account, False = Lookup by Online ID

    NPSSO_CODE = os.getenv("NPSSO_CODE")

    try:
        api = PSN_API(NPSSO_CODE)
        user = PSN_User(USERNAME, api, use_client = USE_CLIENT)
        PSN_Dashboard(user).save()
        print("Execution Completed Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")