# Import Packages
import pandas as pd
import altair as alt

import requests
import json

import os
from dotenv import load_dotenv

from typing import Optional

from IPython.display import display

class SteamAPI:
    """Handles Steam API Interactions"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.steampowered.com"
        self.apps_df = self.getApps()

    def getApps(self) -> pd.DataFrame:
        """Get List of Steam Applications"""
        try:
            response = requests.get(f"{self.base_url}/ISteamApps/GetAppList/v2/")
            response.raise_for_status()

            self.apps_df = pd.DataFrame(response.json()['applist']['apps'])
        except requests.RequestException as e:
            print(f"Failed to Load Steam Apps: {e}")
            self.apps_df = pd.DataFrame()

        return self.apps_df

    def getSteamID(self, username: str) -> Optional[str]:
        """Convert Steam Username to ID"""
        request_url = f"{self.base_url}/ISteamUser/ResolveVanityURL/v0001/"
        params = {'key': self.api_key, 'vanityurl': username}

        try:
            response = requests.get(request_url, params = params)
            response.raise_for_status()

            return response.json().get('response', {}).get('steamid')
        except requests.RequestException as e:
            print(f"Failed to Get Steam ID for {username}: {e}")
            return None

    def getOwned(self, steam_id: str) -> pd.DataFrame:
        """Fetch User's Owned Games"""
        request_url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': self.api_key,
            'steamID': steam_id,
            'format': 'json'
        }

        try:
            response = requests.get(request_url, params = params)
            response.raise_for_status()

            data = response.json()
            if 'games' in data.get('response', {}): # Check for Games
                return self._mergeAppNames(pd.DataFrame(data['response']['games']))
            else:
                print(f"No Games Found for Steam ID: {steam_id}")
                return pd.DataFrame()
        except requests.RequestException as e:
            print(f"Failed to Get Owned Games: {e}")
            return pd.DataFrame()

    def getRecent(self, steam_id: str) -> pd.DataFrame:
        """Fetch User's Recently Played Games"""
        request_url = f"{self.base_url}/IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {
            'key': self.api_key,
            'steamID': steam_id,
            'format': 'json'
        }

        try:
            response = requests.get(request_url, params = params)
            response.raise_for_status()

            data = response.json()
            if 'games' in data.get('response', {}): # Check for Games
                return self._mergeAppNames(pd.DataFrame(data['response']['games']))
            else:
                print(f"No Recently Played Games Found for Steam ID: {steam_id}")
                return pd.DataFrame()
        except requests.RequestException as e:
            print(f"Failed to get Recently Played Games: {e}")
            return pd.DataFrame()

    def getBadges(self, steam_id: str) -> pd.DataFrame:
        """Fetch User's Badges"""
        url = f"{self.base_url}/IPlayerService/GetBadges/v1/"
        params = {
            'key': self.api_key,
            'steamID': steam_id,
            'format': 'json'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'badges_df' in data.get('response', {}): # Check for Badges
                return pd.DataFrame(data['response']['badges_df'])
            else:
                print(f"No Badges Found for Steam ID: {steam_id}")
                return pd.DataFrame()
        except requests.RequestException as e:
            print(f"Failed to Get Badges: {e}")
            return pd.DataFrame()

    def getLevel(self, steam_id: str) -> int:
        """Fetch User's Steam Level"""
        request_url = f"{self.base_url}/IPlayerService/GetSteamLevel/v1/"
        params = {
            'key': self.api_key,
            'steamID': steam_id,
            'format': 'json'
        }

        try:
            response = requests.get(request_url, params=params)
            response.raise_for_status()
            return response.json().get('response', {}).get('player_level', 0)
        except requests.RequestException as e:
            print(f"Failed to Get Player Level: {e}")
            return -1

    def _mergeAppNames(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """Merge Game Data with App Names"""
        if games_df.empty or self.apps_df.empty:
            return games_df
        return games_df.merge(self.apps_df, on = 'appid', how = 'left')


class SteamUser:
    """Represents a Steam User and Their Gaming Data"""

    SKYRIM_ID = 72850
    SKYRIM_SE_ID = 489830
    def __init__(self, username: str, api_client: SteamAPI):
        self.username = username
        self.api_client = api_client

        self.steam_id = None
        self.player_level = 0

        # Steam Data
        self.owned_df = pd.DataFrame()
        self.recent_df = pd.DataFrame()
        self.badges_df = pd.DataFrame()
        self.stats_df = pd.DataFrame()

        self._getData()

    def _getData(self) -> None:
        """Get All User Data from Steam API"""
        try:
            self.steam_id = self.api_client.getSteamID(self.username)

            if not self.steam_id:
                raise ValueError(f"Could Not Find Steam ID for {self.username}")

            self.owned_df = self.api_client.getOwned(self.steam_id)
            self.recent_df = self.api_client.getRecent(self.steam_id)
            self.badges_df = self.api_client.getBadges(self.steam_id)
            self.player_level = self.api_client.getLevel(self.steam_id)

            self._compileStats()

            print(f"Successfully Fetched Data for {self.username}")

            print(f"Owned Games: {len(self.owned_df)}")
            print(f"Player Level: {self.player_level}")

        except Exception as e:
            print(f"Error Fetching User Data: {e}")
            self._loadFromCSV()

    def _loadFromCSV(self) -> None:
        """Load Data from Backup CSV if API Fails"""
        csv_file = f"{self.username}_SteamData.csv"
        if os.path.exists(csv_file):
            print(f"Loading Data from CSV File: {csv_file}")
            self.stats_df = pd.read_csv(csv_file)
            if not self.stats_df.empty:
                self.player_level = self.stats_df['player_level'].iloc[0]
        else:
            print("No Backup Data Available")

    def _compileStats(self) -> None:
        """Compile Stats from all Data sources"""
        if self.owned_df.empty:
            print("No Owned Game Data Available")
            return

        stats_df = self.owned_df.copy()
        if not self.badges_df.empty:
            stats_df = pd.merge(
                stats_df, self.badges_df,
                on = 'appid', how = 'left',
                suffixes = ('', '_badge')
            )
            stats_df = stats_df[[col for col in stats_df.columns if not col.endswith('_badge')]]

        stats_df['player_level'] = self.player_level

        stats_df = self._consolidateSkyrim(stats_df)

        stats_df['playtime_forever'] = (stats_df['playtime_forever'] / 60.0).round(2)

        self.stats_df = stats_df.fillna(0).sort_values('playtime_forever', ascending = False)

        self.saveData()

    def _consolidateSkyrim(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """Consolidate Skyrim and Skyrim SE Data into Single Entry"""

        skyrim_mask = stats_df['appid'] == self.SKYRIM_ID
        skyrim_se_mask = stats_df['appid'] == self.SKYRIM_SE_ID

        if not (skyrim_mask.any() and skyrim_se_mask.any()):
            print("Consolidation Not Required: Either/Both Skyrim / Skyrim SE Data Missing")
            return stats_df

        print("Consolidating Skyrim, Skyrim SE Data...")

        skyrim_data = stats_df[skyrim_mask].copy()
        skyrim_se_data = stats_df[skyrim_se_mask].copy()

        acc_cols = ['playtime_forever', 'completion_time', 'xp']
        max_cols = ['rtime_last_played', 'badgeid', 'communityitemid', 'level']
        avg_cols = ['scarcity']

        for col in acc_cols:
            if col in stats_df.columns:
                skyrim_val = skyrim_data[col].iloc[0] if (not skyrim_data[col].isna().iloc[0]) else 0
                skyrim_se_val = skyrim_se_data[col].iloc[0] if (not skyrim_se_data[col].isna().iloc[0]) else 0

                stats_df.loc[skyrim_mask, col] = skyrim_val + skyrim_se_val

        for col in max_cols:
            if col in stats_df.columns:
                skyrim_val = skyrim_data[col].iloc[0] if (not skyrim_data[col].isna().iloc[0]) else 0
                skyrim_se_val = skyrim_se_data[col].iloc[0] if (not skyrim_se_data[col].isna().iloc[0]) else 0

                stats_df.loc[skyrim_mask, col] = max(skyrim_val, skyrim_se_val)

        for col in avg_cols:
            if col in stats_df.columns:
                skyrim_val = skyrim_data[col].iloc[0] if (not skyrim_data[col].isna().iloc[0]) else 0
                skyrim_se_val = skyrim_se_data[col].iloc[0] if (not skyrim_se_data[col].isna().iloc[0]) else skyrim_val

                stats_df.loc[skyrim_mask, col] = (skyrim_val + skyrim_se_val) / 2

        return stats_df[~skyrim_se_mask] # Remove Skyrim SE Entry

    def saveData(self, filename: Optional[str] = None) -> None:
        """Save User Data to CSV"""
        if filename is None:
            filename = f"{self.username}_SteamData.csv"

        if not self.stats_df.empty:
            self.stats_df.to_csv(filename, index = False)
            print(f"Data Saved to {filename}")

    def getTopData(self, n: int = 15) -> pd.DataFrame:
        """Get Top N games By Playtime"""
        return self.stats_df.nlargest(n, 'playtime_forever')[['name', 'playtime_forever', 'appid']].sort_values('playtime_forever', ascending = False)

    def getNumberPlayed(self) -> int:
        """Get Number of Games with Playtime > 0"""
        return (self.stats_df['playtime_forever'] > 0).sum()

    def getTotalPlaytime(self) -> float:
        """Get Total Playtime Across Games"""
        return self.stats_df['playtime_forever'].sum()

class SteamDashboard:
    """Creates Visualizations for Steam User Data"""

    def __init__(self, user: SteamUser):
        self.user = user
        self.colors = [
            "#00008B", "#32CD32", "#00CED1", "#A8D7E7",
            "#808080", "#FF4500", "#0000FF", "#3D3A38",
            "#800080", "#FFA500","#006400", "#8B0000",
            "#FFD700", "#4682B4", "#2E8B57"
        ]

        self.dashboard = None
        self.generateDashboard()

    def generatePlaytimeChart(self, top_n: int = 15) -> alt.Chart:
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
                text = f"Top {top_n} Games",
                subtitle = f"Total Playtime: {total_playtime:.1f} Hours",
                anchor = 'middle', fontSize = 20, subtitleFontSize = 16
            )
        )

    def generateLevelDisplay(self) -> alt.Chart:
        """Generate Player Level Display"""
        data = pd.DataFrame({
            'Metric': ['Level'],
            'Value': [self.user.player_level]
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
            title = alt.TitleParams(text = 'Level', anchor = 'middle', fontSize = 20)
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
            x = alt.X('Metric:N', axis=None),
            y = alt.value(50),
            text = 'Value:Q'
        ).properties(
            width = 300, height = 150,
            title = alt.TitleParams(text = 'Played', anchor = 'middle', fontSize = 20)
        )

    def generateDashboard(self) -> None:
        """Generate Complete Dashboard"""
        playtime_chart = self.generatePlaytimeChart()
        stats_chart = (
            self.generateLevelDisplay() & self.generatePlayedDisplay()
        ).properties(
            title = alt.TitleParams(text = 'Player Stats', anchor = 'middle', fontSize = 30)
        )

        self.dashboard = (stats_chart | playtime_chart).properties(
            padding = {"left": 250, "right": 250, "top": 0, "bottom": 0},
            title = alt.TitleParams(
                text = f"{self.user.username}'s Steam Dashboard",
                anchor = 'middle', fontSize = 40
            ),
        ).configure_view(
            strokeWidth = 1.5, strokeOpacity = 0
        ).configure_axis(
            labelFontSize = 12, titleFontSize = 16
        ).configure_legend(
            labelFontSize = 12, titleFontSize = 16
        )

    def save(self, filename: Optional[str] = None) -> None:
        """Save Dashboard to File"""
        if self.dashboard is None:
            print("Dashboard Not Generated")
            return

        if filename is None:
            filename = f"{self.user.username}_Dashboard"

        if not os.path.exists('Charts'):
            os.makedirs('Charts')

        # Save as Vega-Lite JSON
        # with open(f"Charts/{filename}.json", 'w') as f:
        #     json.dump(self.dashboard.to_dict(), f, indent = 2)

        # Load Dashboard from JSON File
        with open(f"Charts/{filename}.json", 'r') as f:
            spec = json.load(f)

        self.dashboard = alt.Chart.from_dict(spec) # alt.Chart.from_json(json_str)

        # Save as HTML (Interactive)
        with open(f"Charts/{filename}.html", 'w') as f:
            f.write(self.dashboard.to_html())

        self.dashboard.save(f"Charts/{filename}.png") # Save as PNG (Static)
        self.dashboard.save(f"Charts/{filename}.svg") # Save as SVG (Vector)

if __name__ == '__main__':
    load_dotenv()

    USERNAME = 'Dipto9999'
    API_KEY = os.getenv("STEAM_API_KEY")

    try:
        user = SteamUser(USERNAME, SteamAPI(API_KEY))
        SteamDashboard(user).save()
        print("Execution Completed Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")